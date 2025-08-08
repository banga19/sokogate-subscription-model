from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from ..models.subscription import (
    Subscription, SubscriptionPlan, PreOrder, Customer, Product,
    SubscriptionStatus, PreOrderStatus, PaymentFrequency
)
from ..services.payment_service import PaymentService
from ..services.notification_service import NotificationService

class SubscriptionService:
    def __init__(self, db: Session):
        self.db = db
        self.payment_service = PaymentService()
        self.notification_service = NotificationService()

    async def create_subscription(
        self,
        customer_id: int,
        subscription_plan_id: int,
        payment_method_id: str,
        auto_renew: bool = True
    ) -> Subscription:
        """Create a new subscription for a customer"""
        
        # Validate customer exists
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise ValueError("Customer not found")
        
        # Validate subscription plan exists
        plan = self.db.query(SubscriptionPlan).filter(
            SubscriptionPlan.id == subscription_plan_id,
            SubscriptionPlan.is_active == True
        ).first()
        if not plan:
            raise ValueError("Subscription plan not found or inactive")
        
        # Check if customer already has an active subscription
        existing_subscription = self.db.query(Subscription).filter(
            Subscription.customer_id == customer_id,
            Subscription.status == SubscriptionStatus.ACTIVE.value
        ).first()
        
        if existing_subscription:
            raise ValueError("Customer already has an active subscription")
        
        # Calculate billing dates
        start_date = datetime.utcnow()
        if plan.billing_frequency == PaymentFrequency.MONTHLY.value:
            next_billing_date = start_date + timedelta(days=30)
            end_date = next_billing_date
        elif plan.billing_frequency == PaymentFrequency.QUARTERLY.value:
            next_billing_date = start_date + timedelta(days=90)
            end_date = next_billing_date
        elif plan.billing_frequency == PaymentFrequency.ANNUALLY.value:
            next_billing_date = start_date + timedelta(days=365)
            end_date = next_billing_date
        else:
            raise ValueError("Invalid billing frequency")
        
        # Process initial payment
        try:
            payment_result = await self.payment_service.charge_subscription(
                customer_id=customer_id,
                amount=plan.price,
                payment_method_id=payment_method_id,
                description=f"Subscription to {plan.name}"
            )
        except Exception as e:
            raise ValueError(f"Payment failed: {str(e)}")
        
        # Create subscription
        subscription = Subscription(
            customer_id=customer_id,
            subscription_plan_id=subscription_plan_id,
            status=SubscriptionStatus.ACTIVE.value,
            start_date=start_date,
            end_date=end_date,
            next_billing_date=next_billing_date,
            monthly_preorder_limit=plan.preorder_limit_per_month,
            total_preorder_value_limit=plan.preorder_value_limit,
            payment_method_id=payment_method_id,
            auto_renew=auto_renew
        )
        
        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)
        
        # Send welcome notification
        await self.notification_service.send_subscription_welcome(
            customer_id=customer_id,
            subscription=subscription
        )
        
        return subscription

    async def create_pre_order(
        self,
        subscription_id: int,
        product_id: int,
        quantity: int,
        product_variant_id: Optional[int] = None,
        priority_level: int = 1
    ) -> PreOrder:
        """Create a pre-order for a subscription"""
        
        # Validate subscription
        subscription = self.db.query(Subscription).filter(
            Subscription.id == subscription_id,
            Subscription.status == SubscriptionStatus.ACTIVE.value
        ).first()
        
        if not subscription:
            raise ValueError("Active subscription not found")
        
        # Validate product
        product = self.db.query(Product).filter(
            Product.id == product_id,
            Product.is_active == True,
            Product.is_pre_order_eligible == True
        ).first()
        
        if not product:
            raise ValueError("Product not found or not eligible for pre-order")
        
        # Check pre-order availability window
        now = datetime.utcnow()
        if product.pre_order_start_date and now < product.pre_order_start_date:
            raise ValueError("Pre-order period has not started yet")
        
        if product.pre_order_end_date and now > product.pre_order_end_date:
            raise ValueError("Pre-order period has ended")
        
        # Check product pre-order limits
        if product.pre_order_limit and (product.current_pre_orders + quantity) > product.pre_order_limit:
            raise ValueError("Pre-order quantity exceeds available limit")
        
        # Check subscription limits
        await self._validate_subscription_limits(subscription, product, quantity)
        
        # Calculate pricing
        unit_price = product.pre_order_price or product.base_price
        
        # Apply subscription discount
        plan = subscription.subscription_plan
        discount_applied = unit_price * (plan.discount_percentage / 100)
        discounted_price = unit_price - discount_applied
        total_amount = discounted_price * quantity
        
        # Create pre-order
        pre_order = PreOrder(
            subscription_id=subscription_id,
            customer_id=subscription.customer_id,
            product_id=product_id,
            product_variant_id=product_variant_id,
            quantity=quantity,
            unit_price=unit_price,
            discount_applied=discount_applied * quantity,
            total_amount=total_amount,
            status=PreOrderStatus.PENDING.value,
            expected_availability_date=product.expected_availability_date,
            pre_order_deadline=product.pre_order_end_date,
            priority_level=priority_level
        )
        
        self.db.add(pre_order)
        
        # Update counters
        product.current_pre_orders += quantity
        subscription.current_month_preorders += 1
        subscription.current_preorder_value += total_amount
        
        self.db.commit()
        self.db.refresh(pre_order)
        
        # Send confirmation notification
        await self.notification_service.send_pre_order_confirmation(
            customer_id=subscription.customer_id,
            pre_order=pre_order
        )
        
        return pre_order

    async def _validate_subscription_limits(
        self, 
        subscription: Subscription, 
        product: Product, 
        quantity: int
    ):
        """Validate subscription pre-order limits"""
        
        # Get current month stats
        current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        current_month_orders = self.db.query(PreOrder).filter(
            PreOrder.subscription_id == subscription.id,
            PreOrder.created_at >= current_month_start,
            PreOrder.status != PreOrderStatus.CANCELLED.value
        ).count()
        
        current_month_value = self.db.query(func.sum(PreOrder.total_amount)).filter(
            PreOrder.subscription_id == subscription.id,
            PreOrder.created_at >= current_month_start,
            PreOrder.status != PreOrderStatus.CANCELLED.value
        ).scalar() or 0.0
        
        # Check order count limit
        if subscription.monthly_preorder_limit > 0:
            if current_month_orders >= subscription.monthly_preorder_limit:
                raise ValueError("Monthly pre-order limit exceeded")
        
        # Check value limit
        unit_price = product.pre_order_price or product.base_price
        plan = subscription.subscription_plan
        discount_applied = unit_price * (plan.discount_percentage / 100)
        discounted_price = unit_price - discount_applied
        order_total = discounted_price * quantity
        
        if subscription.total_preorder_value_limit > 0:
            if (current_month_value + order_total) > subscription.total_preorder_value_limit:
                raise ValueError("Monthly pre-order value limit exceeded")

    async def pause_subscription(self, subscription_id: int):
        """Pause a subscription"""
        subscription = self.db.query(Subscription).filter(
            Subscription.id == subscription_id
        ).first()
        
        if not subscription:
            raise ValueError("Subscription not found")
        
        if subscription.status != SubscriptionStatus.ACTIVE.value:
            raise ValueError("Can only pause active subscriptions")
        
        subscription.status = SubscriptionStatus.PAUSED.value
        self.db.commit()
        
        await self.notification_service.send_subscription_paused(
            customer_id=subscription.customer_id,
            subscription=subscription
        )

    async def resume_subscription(self, subscription_id: int):
        """Resume a paused subscription"""
        subscription = self.db.query(Subscription).filter(
            Subscription.id == subscription_id
        ).first()
        
        if not subscription:
            raise ValueError("Subscription not found")
        
        if subscription.status != SubscriptionStatus.PAUSED.value:
            raise ValueError("Can only resume paused subscriptions")
        
        subscription.status = SubscriptionStatus.ACTIVE.value
        self.db.commit()
        
        await self.notification_service.send_subscription_resumed(
            customer_id=subscription.customer_id,
            subscription=subscription
        )

    async def cancel_subscription(self, subscription_id: int, immediate: bool = False):
        """Cancel a subscription"""
        subscription = self.db.query(Subscription).filter(
            Subscription.id == subscription_id
        ).first()
        
        if not subscription:
            raise ValueError("Subscription not found")
        
        if subscription.status == SubscriptionStatus.CANCELLED.value:
            raise ValueError("Subscription already cancelled")
        
        if immediate:
            subscription.status = SubscriptionStatus.CANCELLED.value
            subscription.end_date = datetime.utcnow()
        else:
            # Cancel at end of billing period
            subscription.auto_renew = False
            subscription.status = SubscriptionStatus.CANCELLED.value
        
        # Cancel pending pre-orders
        pending_pre_orders = self.db.query(PreOrder).filter(
            PreOrder.subscription_id == subscription_id,
            PreOrder.status == PreOrderStatus.PENDING.value
        ).all()
        
        for pre_order in pending_pre_orders:
            await self.cancel_pre_order(pre_order.id)
        
        self.db.commit()
        
        await self.notification_service.send_subscription_cancelled(
            customer_id=subscription.customer_id,
            subscription=subscription,
            immediate=immediate
        )

    async def cancel_pre_order(self, pre_order_id: int):
        """Cancel a pre-order"""
        pre_order = self.db.query(PreOrder).filter(
            PreOrder.id == pre_order_id
        ).first()
        
        if not pre_order:
            raise ValueError("Pre-order not found")
        
        if pre_order.status == PreOrderStatus.CANCELLED.value:
            raise ValueError("Pre-order already cancelled")
        
        if pre_order.status in [PreOrderStatus.PROCESSING.value, PreOrderStatus.FULFILLED.value]:
            raise ValueError("Cannot cancel pre-order in current status")
        
        # Update status
        pre_order.status = PreOrderStatus.CANCELLED.value
        
        # Update counters
        product = pre_order.product
        subscription = pre_order.subscription
        
        product.current_pre_orders -= pre_order.quantity
        subscription.current_month_preorders -= 1
        subscription.current_preorder_value -= pre_order.total_amount
        
        # Process refund if payment was made
        if pre_order.payment_status == "charged":
            await self.payment_service.refund_payment(
                payment_intent_id=pre_order.payment_intent_id,
                amount=pre_order.total_amount
            )
            pre_order.payment_status = "refunded"
        
        self.db.commit()
        
        await self.notification_service.send_pre_order_cancelled(
            customer_id=pre_order.customer_id,
            pre_order=pre_order
        )

    async def process_billing_cycle(self):
        """Process recurring billing for subscriptions"""
        today = datetime.utcnow().date()
        
        # Find subscriptions due for billing
        due_subscriptions = self.db.query(Subscription).filter(
            Subscription.status == SubscriptionStatus.ACTIVE.value,
            Subscription.auto_renew == True,
            func.date(Subscription.next_billing_date) <= today
        ).all()
        
        for subscription in due_subscriptions:
            try:
                await self._process_subscription_renewal(subscription)
            except Exception as e:
                print(f"Failed to process subscription {subscription.id}: {str(e)}")
                await self.notification_service.send_billing_failed(
                    customer_id=subscription.customer_id,
                    subscription=subscription,
                    error=str(e)
                )

    async def _process_subscription_renewal(self, subscription: Subscription):
        """Process renewal for a single subscription"""
        plan = subscription.subscription_plan
        
        # Attempt payment
        payment_result = await self.payment_service.charge_subscription(
            customer_id=subscription.customer_id,
            amount=plan.price,
            payment_method_id=subscription.payment_method_id,
            description=f"Subscription renewal - {plan.name}"
        )
        
        # Update billing dates
        if plan.billing_frequency == PaymentFrequency.MONTHLY.value:
            subscription.next_billing_date += timedelta(days=30)
            subscription.end_date = subscription.next_billing_date
        elif plan.billing_frequency == PaymentFrequency.QUARTERLY.value:
            subscription.next_billing_date += timedelta(days=90)
            subscription.end_date = subscription.next_billing_date
        elif plan.billing_frequency == PaymentFrequency.ANNUALLY.value:
            subscription.next_billing_date += timedelta(days=365)
            subscription.end_date = subscription.next_billing_date
        
        # Reset monthly counters
        subscription.current_month_preorders = 0
        subscription.current_preorder_value = 0.0
        
        self.db.commit()
        
        await self.notification_service.send_billing_success(
            customer_id=subscription.customer_id,
            subscription=subscription,
            amount=plan.price
        )

    def get_subscription_analytics(self, subscription_id: int) -> dict:
        """Get analytics for a subscription"""
        subscription = self.db.query(Subscription).filter(
            Subscription.id == subscription_id
        ).first()
        
        if not subscription:
            raise ValueError("Subscription not found")
        
        # Calculate various metrics
        total_pre_orders = self.db.query(PreOrder).filter(
            PreOrder.subscription_id == subscription_id
        ).count()
        
        total_value = self.db.query(func.sum(PreOrder.total_amount)).filter(
            PreOrder.subscription_id == subscription_id,
            PreOrder.status != PreOrderStatus.CANCELLED.value
        ).scalar() or 0.0
        
        avg_order_value = total_value / total_pre_orders if total_pre_orders > 0 else 0.0
        
        # Monthly breakdown
        current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        monthly_orders = self.db.query(PreOrder).filter(
            PreOrder.subscription_id == subscription_id,
            PreOrder.created_at >= current_month_start
        ).count()
        
        monthly_value = self.db.query(func.sum(PreOrder.total_amount)).filter(
            PreOrder.subscription_id == subscription_id,
            PreOrder.created_at >= current_month_start,
            PreOrder.status != PreOrderStatus.CANCELLED.value
        ).scalar() or 0.0
        
        return {
            "subscription_id": subscription_id,
            "total_pre_orders": total_pre_orders,
            "total_order_value": total_value,
            "average_order_value": avg_order_value,
            "current_month_orders": monthly_orders,
            "current_month_value": monthly_value,
            "subscription_start_date": subscription.start_date,
            "subscription_status": subscription.status,
            "plan_name": subscription.subscription_plan.name
        }
