from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr
from models.subscription import Customer
from database import get_db

router = APIRouter(prefix="/api/v1/customers", tags=["customers"])

class CustomerCreateRequest(BaseModel):
    company_name: str
    contact_email: EmailStr
    contact_phone: Optional[str] = None
    business_type: Optional[str] = None
    tax_id: Optional[str] = None
    billing_address: Optional[dict] = None
    shipping_address: Optional[dict] = None
    credit_limit: float = 0.0
    payment_terms: str = "net_30"

class CustomerUpdateRequest(BaseModel):
    company_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    business_type: Optional[str] = None
    tax_id: Optional[str] = None
    billing_address: Optional[dict] = None
    shipping_address: Optional[dict] = None
    credit_limit: Optional[float] = None
    payment_terms: Optional[str] = None
    is_active: Optional[bool] = None

class CustomerResponse(BaseModel):
    id: int
    company_name: str
    contact_email: str
    contact_phone: Optional[str]
    business_type: Optional[str]
    tax_id: Optional[str]
    billing_address: Optional[dict]
    shipping_address: Optional[dict]
    is_active: bool
    credit_limit: float
    payment_terms: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

@router.post("/", response_model=CustomerResponse)
async def create_customer(request: CustomerCreateRequest, db: Session = Depends(get_db)):
    """Create a new customer"""
    # Check if email already exists
    existing_customer = db.query(Customer).filter(Customer.contact_email == request.contact_email).first()
    if existing_customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    db_customer = Customer(**request.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

@router.get("/", response_model=List[CustomerResponse])
async def get_customers(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get all customers with optional filtering"""
    query = db.query(Customer)

    if search:
        query = query.filter(
            (Customer.company_name.ilike(f"%{search}%")) |
            (Customer.contact_email.ilike(f"%{search}%"))
        )

    if is_active is not None:
        query = query.filter(Customer.is_active == is_active)

    customers = query.offset(skip).limit(limit).all()
    return customers

@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: int, db: Session = Depends(get_db)):
    """Get a specific customer"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return customer

@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    request: CustomerUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update a customer"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    # Check if email is being changed and if it's already taken
    if request.contact_email and request.contact_email != customer.contact_email:
        existing_customer = db.query(Customer).filter(
            Customer.contact_email == request.contact_email,
            Customer.id != customer_id
        ).first()
        if existing_customer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )

    update_data = request.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(customer, field, value)

    db.commit()
    db.refresh(customer)
    return customer

@router.delete("/{customer_id}")
async def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    """Delete a customer (soft delete by setting is_active to False)"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    customer.is_active = False
    db.commit()
    return {"message": "Customer deactivated successfully"}

@router.get("/{customer_id}/stats")
async def get_customer_stats(customer_id: int, db: Session = Depends(get_db)):
    """Get customer statistics"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    # Get subscription stats
    active_subscriptions = len([s for s in customer.subscriptions if s.status == "active"])
    total_subscriptions = len(customer.subscriptions)

    # Get pre-order stats
    total_preorders = len(customer.pre_orders)
    pending_preorders = len([p for p in customer.pre_orders if p.status == "pending"])

    return {
        "customer_id": customer_id,
        "active_subscriptions": active_subscriptions,
        "total_subscriptions": total_subscriptions,
        "total_preorders": total_preorders,
        "pending_preorders": pending_preorders
    }