from datetime import datetime, timedelta
from enum import Enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class SubscriptionStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused" 
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class PreOrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"

class SubscriptionTier(Enum):
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class PaymentFrequency(Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    subscription_plan_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=False)
    
    # Subscription details
    status = Column(String(20), default=SubscriptionStatus.ACTIVE.value)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)
    next_billing_date = Column(DateTime)
    
    # Pre-order allowances
    monthly_preorder_limit = Column(Integer, default=0)  # 0 = unlimited
    current_month_preorders = Column(Integer, default=0)
    total_preorder_value_limit = Column(Float, default=0.0)  # 0.0 = unlimited
    current_preorder_value = Column(Float, default=0.0)
    
    # Payment
    payment_method_id = Column(String(100))
    auto_renew = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="subscriptions")
    subscription_plan = relationship("SubscriptionPlan", back_populates="subscriptions")
    pre_orders = relationship("PreOrder", back_populates="subscription")

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    tier = Column(String(20), nullable=False)  # basic, premium, enterprise
    description = Column(Text)
    
    # Pricing
    price = Column(Float, nullable=False)
    billing_frequency = Column(String(20), nullable=False)  # monthly, quarterly, annually
    
    # Pre-order benefits
    preorder_limit_per_month = Column(Integer, default=0)  # 0 = unlimited
    preorder_value_limit = Column(Float, default=0.0)  # 0.0 = unlimited
    early_access_days = Column(Integer, default=0)  # days before general availability
    discount_percentage = Column(Float, default=0.0)  # discount on pre-orders
    
    # Features
    priority_support = Column(Boolean, default=False)
    dedicated_account_manager = Column(Boolean, default=False)
    custom_reporting = Column(Boolean, default=False)
    api_access = Column(Boolean, default=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="subscription_plan")

class PreOrder(Base):
    __tablename__ = "pre_orders"
    
    id = Column(Integer, primary_key=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    
    # Product details
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    product_variant_id = Column(Integer, ForeignKey("product_variants.id"))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    discount_applied = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    
    # Pre-order specifics
    status = Column(String(20), default=PreOrderStatus.PENDING.value)
    expected_availability_date = Column(DateTime)
    pre_order_deadline = Column(DateTime)
    priority_level = Column(Integer, default=1)  # 1 = highest, 5 = lowest
    
    # Fulfillment
    estimated_delivery_date = Column(DateTime)
    actual_delivery_date = Column(DateTime)
    tracking_number = Column(String(100))
    
    # Payment
    payment_status = Column(String(20), default="pending")  # pending, authorized, charged, refunded
    payment_intent_id = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscription = relationship("Subscription", back_populates="pre_orders")
    customer = relationship("Customer", back_populates="pre_orders")
    product = relationship("Product", back_populates="pre_orders")

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True)
    company_name = Column(String(200), nullable=False)
    contact_email = Column(String(100), nullable=False, unique=True)
    contact_phone = Column(String(20))
    
    # Business details
    business_type = Column(String(50))
    tax_id = Column(String(50))
    billing_address = Column(JSON)
    shipping_address = Column(JSON)
    
    # Account status
    is_active = Column(Boolean, default=True)
    credit_limit = Column(Float, default=0.0)
    payment_terms = Column(String(20), default="net_30")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="customer")
    pre_orders = relationship("PreOrder", back_populates="customer")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    sku = Column(String(100), unique=True)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey("categories.id"))
    
    # Pre-order specific
    is_pre_order_eligible = Column(Boolean, default=False)
    pre_order_start_date = Column(DateTime)
    pre_order_end_date = Column(DateTime)
    expected_availability_date = Column(DateTime)
    pre_order_limit = Column(Integer)  # Max units available for pre-order
    current_pre_orders = Column(Integer, default=0)
    
    # Pricing
    base_price = Column(Float, nullable=False)
    pre_order_price = Column(Float)  # Special pre-order pricing
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    pre_orders = relationship("PreOrder", back_populates="product")
