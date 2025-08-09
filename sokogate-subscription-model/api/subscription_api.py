from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, validator
from models.subscription import Subscription, SubscriptionPlan, PreOrder, Customer, Product
from ..services.subscription_service import SubscriptionService
from ..database import get_db

router = APIRouter(prefix="/api/v1/subscriptions", tags=["subscriptions"])

# Pydantic schemas for request/response models
class SubscriptionPlanResponse(BaseModel):
    id: int
    name: str
    tier: str
    description: Optional[str]
    price: float
    billing_frequency: str
    preorder_limit_per_month: int
    preorder_value_limit: float
    early_access_days: int
    discount_percentage: float
    priority_support: bool
    dedicated_account_manager: bool
    custom_reporting: bool
    api_access: bool
    is_active: bool

    class Config:
        from_attributes = True

class SubscriptionCreateRequest(BaseModel):
    customer_id: int
    subscription_plan_id: int
    payment_method_id: str
    auto_renew: bool = True

class SubscriptionResponse(BaseModel):
    id: int
    customer_id: int
    subscription_plan_id: int
    status: str
    start_date: datetime
    end_date: Optional[datetime]
    next_billing_date: Optional[datetime]
    monthly_preorder_limit: int
    current_month_preorders: int
    total_preorder_value_limit: float
    current_preorder_value: float
    auto_renew: bool
    subscription_plan: SubscriptionPlanResponse

    class Config:
        from_attributes = True

class PreOrderCreateRequest(BaseModel):
    product_id: int
    product_variant_id: Optional[int] = None
    quantity: int
    priority_level: int = 1

    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v

    @validator('priority_level')
    def validate_priority(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Priority level must be between 1 and 5')
        return v

class PreOrderResponse(BaseModel):
    id: int
    subscription_id: int
    customer_id: int
    product_id: int
    product_variant_id: Optional[int]
    quantity: int
    unit_price: float
    discount_applied: float
    total_amount: float
    status: str
    expected_availability_date: Optional[datetime]
    pre_order_deadline: Optional[datetime]
    priority_level: int
    estimated_delivery_date: Optional[datetime]
    payment_status: str
    created_at: datetime

    class Config:
        from_attributes = True

# Subscription Plan endpoints
@router.get("/plans", response_model=List[SubscriptionPlanResponse])
async def get_subscription_plans(
    tier: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all available subscription plans"""
    query = db.query(SubscriptionPlan).filter(SubscriptionPlan.is_active == True)
    
    if tier:
        query = query.filter(SubscriptionPlan.tier == tier)
    
    plans = query.all()
    return plans

@router.get("/plans/{plan_id}", response_model=SubscriptionPlanResponse)
async def get_subscription_plan(
    plan_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific subscription plan"""
    plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.id == plan_id,
        SubscriptionPlan.is_active == True
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found"
        )
    
    return plan

# Subscription management endpoints
@router.post("/", response_model=SubscriptionResponse)
async def create_subscription(
    request: SubscriptionCreateRequest,
    db: Session = Depends(get_db)
):
    """Create a new subscription"""
    service = SubscriptionService(db)
    
    try:
        subscription = await service.create_subscription(
            customer_id=request.customer_id,
            subscription_plan_id=request.subscription_plan_id,
            payment_method_id=request.payment_method_id,
            auto_renew=request.auto_renew
        )
        return subscription
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/customer/{customer_id}", response_model=List[SubscriptionResponse])
async def get_customer_subscriptions(
    customer_id: int,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all subscriptions for a customer"""
    query = db.query(Subscription).filter(Subscription.customer_id == customer_id)
    
    if status:
        query = query.filter(Subscription.status == status)
    
    subscriptions = query.all()
    return subscriptions

@router.get("/{subscription_id}", response_model=SubscriptionResponse)
async def get_subscription(
    subscription_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific subscription"""
    subscription = db.query(Subscription).filter(
        Subscription.id == subscription_id
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    return subscription

@router.put("/{subscription_id}/pause")
async def pause_subscription(
    subscription_id: int,
    db: Session = Depends(get_db)
):
    """Pause a subscription"""
    service = SubscriptionService(db)
    
    try:
        await service.pause_subscription(subscription_id)
        return {"message": "Subscription paused successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{subscription_id}/resume")
async def resume_subscription(
    subscription_id: int,
    db: Session = Depends(get_db)
):
    """Resume a paused subscription"""
    service = SubscriptionService(db)
    
    try:
        await service.resume_subscription(subscription_id)
        return {"message": "Subscription resumed successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{subscription_id}")
async def cancel_subscription(
    subscription_id: int,
    immediate: bool = False,
    db: Session = Depends(get_db)
):
    """Cancel a subscription"""
    service = SubscriptionService(db)
    
    try:
        await service.cancel_subscription(subscription_id, immediate)
        return {"message": "Subscription cancelled successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Pre-order endpoints
@router.post("/{subscription_id}/pre-orders", response_model=PreOrderResponse)
async def create_pre_order(
    subscription_id: int,
    request: PreOrderCreateRequest,
    db: Session = Depends(get_db)
):
    """Create a new pre-order"""
    service = SubscriptionService(db)
    
    try:
        pre_order = await service.create_pre_order(
            subscription_id=subscription_id,
            product_id=request.product_id,
            product_variant_id=request.product_variant_id,
            quantity=request.quantity,
            priority_level=request.priority_level
        )
        return pre_order
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{subscription_id}/pre-orders", response_model=List[PreOrderResponse])
async def get_subscription_pre_orders(
    subscription_id: int,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all pre-orders for a subscription"""
    query = db.query(PreOrder).filter(PreOrder.subscription_id == subscription_id)
    
    if status:
        query = query.filter(PreOrder.status == status)
    
    pre_orders = query.order_by(PreOrder.created_at.desc()).all()
    return pre_orders

@router.get("/pre-orders/{pre_order_id}", response_model=PreOrderResponse)
async def get_pre_order(
    pre_order_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific pre-order"""
    pre_order = db.query(PreOrder).filter(PreOrder.id == pre_order_id).first()
    
    if not pre_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pre-order not found"
        )
    
    return pre_order

@router.put("/pre-orders/{pre_order_id}/cancel")
async def cancel_pre_order(
    pre_order_id: int,
    db: Session = Depends(get_db)
):
    """Cancel a pre-order"""
    service = SubscriptionService(db)
    
    try:
        await service.cancel_pre_order(pre_order_id)
        return {"message": "Pre-order cancelled successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{subscription_id}/usage")
async def get_subscription_usage(
    subscription_id: int,
    db: Session = Depends(get_db)
):
    """Get subscription usage statistics"""
    subscription = db.query(Subscription).filter(
        Subscription.id == subscription_id
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    # Calculate usage statistics
    current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    monthly_pre_orders = db.query(PreOrder).filter(
        PreOrder.subscription_id == subscription_id,
        PreOrder.created_at >= current_month_start,
        PreOrder.status != "cancelled"
    ).count()
    
    monthly_pre_order_value = db.query(PreOrder).filter(
        PreOrder.subscription_id == subscription_id,
        PreOrder.created_at >= current_month_start,
        PreOrder.status != "cancelled"
    ).with_entities(db.func.sum(PreOrder.total_amount)).scalar() or 0.0
    
    return {
        "subscription_id": subscription_id,
        "current_month_preorders": monthly_pre_orders,
        "monthly_preorder_limit": subscription.monthly_preorder_limit,
        "current_preorder_value": monthly_pre_order_value,
        "total_preorder_value_limit": subscription.total_preorder_value_limit,
        "usage_percentage": {
            "orders": (monthly_pre_orders / subscription.monthly_preorder_limit * 100) if subscription.monthly_preorder_limit > 0 else 0,
            "value": (monthly_pre_order_value / subscription.total_preorder_value_limit * 100) if subscription.total_preorder_value_limit > 0 else 0
        }
    }
