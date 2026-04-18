from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from models.subscription import Product
from database import get_db

router = APIRouter(prefix="/api/v1/products", tags=["products"])

class ProductCreateRequest(BaseModel):
    name: str
    sku: str
    description: Optional[str] = None
    is_pre_order_eligible: bool = False
    pre_order_start_date: Optional[datetime] = None
    pre_order_end_date: Optional[datetime] = None
    expected_availability_date: Optional[datetime] = None
    pre_order_limit: Optional[int] = None
    base_price: float
    pre_order_price: Optional[float] = None

class ProductUpdateRequest(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    description: Optional[str] = None
    is_pre_order_eligible: Optional[bool] = None
    pre_order_start_date: Optional[datetime] = None
    pre_order_end_date: Optional[datetime] = None
    expected_availability_date: Optional[datetime] = None
    pre_order_limit: Optional[int] = None
    base_price: Optional[float] = None
    pre_order_price: Optional[float] = None
    is_active: Optional[bool] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    sku: str
    description: Optional[str]
    is_pre_order_eligible: bool
    pre_order_start_date: Optional[datetime]
    pre_order_end_date: Optional[datetime]
    expected_availability_date: Optional[datetime]
    pre_order_limit: Optional[int]
    current_pre_orders: int
    base_price: float
    pre_order_price: Optional[float]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

@router.post("/", response_model=ProductResponse)
async def create_product(request: ProductCreateRequest, db: Session = Depends(get_db)):
    """Create a new product"""
    # Check if SKU already exists
    existing_product = db.query(Product).filter(Product.sku == request.sku).first()
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SKU already exists"
        )

    db_product = Product(**request.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/", response_model=List[ProductResponse])
async def get_products(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_pre_order_eligible: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get all products with optional filtering"""
    query = db.query(Product)

    if search:
        query = query.filter(
            (Product.name.ilike(f"%{search}%")) |
            (Product.sku.ilike(f"%{search}%")) |
            (Product.description.ilike(f"%{search}%"))
        )

    if is_active is not None:
        query = query.filter(Product.is_active == is_active)

    if is_pre_order_eligible is not None:
        query = query.filter(Product.is_pre_order_eligible == is_pre_order_eligible)

    products = query.offset(skip).limit(limit).all()
    return products

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a specific product"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    request: ProductUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update a product"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Check if SKU is being changed and if it's already taken
    if request.sku and request.sku != product.sku:
        existing_product = db.query(Product).filter(
            Product.sku == request.sku,
            Product.id != product_id
        ).first()
        if existing_product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SKU already in use"
            )

    update_data = request.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Delete a product (soft delete by setting is_active to False)"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    product.is_active = False
    db.commit()
    return {"message": "Product deactivated successfully"}

@router.get("/{product_id}/availability")
async def get_product_availability(product_id: int, db: Session = Depends(get_db)):
    """Get product availability information"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    remaining_slots = None
    if product.pre_order_limit:
        remaining_slots = product.pre_order_limit - product.current_pre_orders

    return {
        "product_id": product_id,
        "is_available_for_preorder": product.is_pre_order_eligible and product.is_active,
        "remaining_slots": remaining_slots,
        "current_pre_orders": product.current_pre_orders,
        "pre_order_limit": product.pre_order_limit,
        "pre_order_start_date": product.pre_order_start_date,
        "pre_order_end_date": product.pre_order_end_date,
        "expected_availability_date": product.expected_availability_date
    }