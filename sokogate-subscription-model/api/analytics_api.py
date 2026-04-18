from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
from models.subscription import Subscription, SubscriptionPlan, PreOrder, Customer, Product
from database import get_db

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

class AnalyticsSummary(BaseModel):
    total_customers: int
    active_customers: int
    total_subscriptions: int
    active_subscriptions: int
    total_preorders: int
    pending_preorders: int
    total_revenue: float
    monthly_revenue: float

class SubscriptionAnalytics(BaseModel):
    plan_name: str
    tier: str
    subscriber_count: int
    revenue: float
    percentage: float

class PreOrderAnalytics(BaseModel):
    status: str
    count: int
    total_value: float
    percentage: float

class RevenueAnalytics(BaseModel):
    period: str
    revenue: float
    subscriptions: int
    preorders: int

@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(db: Session = Depends(get_db)):
    """Get overall analytics summary"""
    # Customer stats
    total_customers = db.query(func.count(Customer.id)).scalar()
    active_customers = db.query(func.count(Customer.id)).filter(Customer.is_active == True).scalar()

    # Subscription stats
    total_subscriptions = db.query(func.count(Subscription.id)).scalar()
    active_subscriptions = db.query(func.count(Subscription.id)).filter(Subscription.status == "active").scalar()

    # Pre-order stats
    total_preorders = db.query(func.count(PreOrder.id)).scalar()
    pending_preorders = db.query(func.count(PreOrder.id)).filter(PreOrder.status == "pending").scalar()

    # Revenue calculations
    subscription_revenue = db.query(func.sum(SubscriptionPlan.price)).join(Subscription).filter(
        Subscription.status == "active"
    ).scalar() or 0.0

    preorder_revenue = db.query(func.sum(PreOrder.total_amount)).scalar() or 0.0
    total_revenue = subscription_revenue + preorder_revenue

    # Monthly revenue (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    monthly_subscription_revenue = db.query(func.sum(SubscriptionPlan.price)).join(Subscription).filter(
        Subscription.status == "active",
        Subscription.created_at >= thirty_days_ago
    ).scalar() or 0.0

    monthly_preorder_revenue = db.query(func.sum(PreOrder.total_amount)).filter(
        PreOrder.created_at >= thirty_days_ago
    ).scalar() or 0.0

    monthly_revenue = monthly_subscription_revenue + monthly_preorder_revenue

    return AnalyticsSummary(
        total_customers=total_customers,
        active_customers=active_customers,
        total_subscriptions=total_subscriptions,
        active_subscriptions=active_subscriptions,
        total_preorders=total_preorders,
        pending_preorders=pending_preorders,
        total_revenue=total_revenue,
        monthly_revenue=monthly_revenue
    )

@router.get("/subscriptions", response_model=List[SubscriptionAnalytics])
async def get_subscription_analytics(db: Session = Depends(get_db)):
    """Get subscription plan analytics"""
    # Get subscription counts and revenue by plan
    results = db.query(
        SubscriptionPlan.name,
        SubscriptionPlan.tier,
        func.count(Subscription.id).label('subscriber_count'),
        func.sum(SubscriptionPlan.price).label('revenue')
    ).join(Subscription).filter(
        Subscription.status == "active"
    ).group_by(SubscriptionPlan.id, SubscriptionPlan.name, SubscriptionPlan.tier).all()

    total_subscribers = sum(result.subscriber_count for result in results)

    analytics = []
    for result in results:
        percentage = (result.subscriber_count / total_subscribers * 100) if total_subscribers > 0 else 0
        analytics.append(SubscriptionAnalytics(
            plan_name=result.name,
            tier=result.tier,
            subscriber_count=result.subscriber_count,
            revenue=result.revenue or 0.0,
            percentage=round(percentage, 2)
        ))

    return analytics

@router.get("/preorders", response_model=List[PreOrderAnalytics])
async def get_preorder_analytics(db: Session = Depends(get_db)):
    """Get pre-order status analytics"""
    # Get pre-order counts and values by status
    results = db.query(
        PreOrder.status,
        func.count(PreOrder.id).label('count'),
        func.sum(PreOrder.total_amount).label('total_value')
    ).group_by(PreOrder.status).all()

    total_preorders = sum(result.count for result in results)

    analytics = []
    for result in results:
        percentage = (result.count / total_preorders * 100) if total_preorders > 0 else 0
        analytics.append(PreOrderAnalytics(
            status=result.status,
            count=result.count,
            total_value=result.total_value or 0.0,
            percentage=round(percentage, 2)
        ))

    return analytics

@router.get("/revenue/{period}")
async def get_revenue_analytics(
    period: str,  # daily, weekly, monthly
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get revenue analytics over time"""
    if period not in ["daily", "weekly", "monthly"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Period must be daily, weekly, or monthly"
        )

    # Calculate date ranges
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    revenue_data = []

    if period == "daily":
        # Group by day
        current_date = start_date
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)

            daily_subscription_revenue = db.query(func.sum(SubscriptionPlan.price)).join(Subscription).filter(
                Subscription.status == "active",
                Subscription.created_at >= current_date,
                Subscription.created_at < next_date
            ).scalar() or 0.0

            daily_preorder_revenue = db.query(func.sum(PreOrder.total_amount)).filter(
                PreOrder.created_at >= current_date,
                PreOrder.created_at < next_date
            ).scalar() or 0.0

            daily_subscriptions = db.query(func.count(Subscription.id)).filter(
                Subscription.created_at >= current_date,
                Subscription.created_at < next_date
            ).scalar()

            daily_preorders = db.query(func.count(PreOrder.id)).filter(
                PreOrder.created_at >= current_date,
                PreOrder.created_at < next_date
            ).scalar()

            revenue_data.append({
                "period": current_date.strftime("%Y-%m-%d"),
                "revenue": daily_subscription_revenue + daily_preorder_revenue,
                "subscriptions": daily_subscriptions,
                "preorders": daily_preorders
            })

            current_date = next_date

    elif period == "weekly":
        # Group by week
        current_date = start_date
        while current_date <= end_date:
            next_date = current_date + timedelta(days=7)

            weekly_subscription_revenue = db.query(func.sum(SubscriptionPlan.price)).join(Subscription).filter(
                Subscription.status == "active",
                Subscription.created_at >= current_date,
                Subscription.created_at < next_date
            ).scalar() or 0.0

            weekly_preorder_revenue = db.query(func.sum(PreOrder.total_amount)).filter(
                PreOrder.created_at >= current_date,
                PreOrder.created_at < next_date
            ).scalar() or 0.0

            weekly_subscriptions = db.query(func.count(Subscription.id)).filter(
                Subscription.created_at >= current_date,
                Subscription.created_at < next_date
            ).scalar()

            weekly_preorders = db.query(func.count(PreOrder.id)).filter(
                PreOrder.created_at >= current_date,
                PreOrder.created_at < next_date
            ).scalar()

            revenue_data.append({
                "period": f"{current_date.strftime('%Y-%m-%d')} to {(next_date - timedelta(days=1)).strftime('%Y-%m-%d')}",
                "revenue": weekly_subscription_revenue + weekly_preorder_revenue,
                "subscriptions": weekly_subscriptions,
                "preorders": weekly_preorders
            })

            current_date = next_date

    return {"data": revenue_data, "period": period, "days": days}

@router.get("/customers/top")
async def get_top_customers(limit: int = 10, db: Session = Depends(get_db)):
    """Get top customers by revenue"""
    # Get customers with highest preorder value
    results = db.query(
        Customer.id,
        Customer.company_name,
        Customer.contact_email,
        func.sum(PreOrder.total_amount).label('total_spent'),
        func.count(PreOrder.id).label('total_orders')
    ).join(PreOrder).group_by(
        Customer.id, Customer.company_name, Customer.contact_email
    ).order_by(func.sum(PreOrder.total_amount).desc()).limit(limit).all()

    top_customers = []
    for result in results:
        top_customers.append({
            "id": result.id,
            "company_name": result.company_name,
            "contact_email": result.contact_email,
            "total_spent": result.total_spent or 0.0,
            "total_orders": result.total_orders
        })

    return {"top_customers": top_customers}

@router.get("/products/top")
async def get_top_products(limit: int = 10, db: Session = Depends(get_db)):
    """Get top products by pre-orders"""
    # Get products with most pre-orders
    results = db.query(
        Product.id,
        Product.name,
        Product.sku,
        func.count(PreOrder.id).label('total_preorders'),
        func.sum(PreOrder.total_amount).label('total_revenue')
    ).join(PreOrder).group_by(
        Product.id, Product.name, Product.sku
    ).order_by(func.count(PreOrder.id).desc()).limit(limit).all()

    top_products = []
    for result in results:
        top_products.append({
            "id": result.id,
            "name": result.name,
            "sku": result.sku,
            "total_preorders": result.total_preorders,
            "total_revenue": result.total_revenue or 0.0
        })

    return {"top_products": top_products}