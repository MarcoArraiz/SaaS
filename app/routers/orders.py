from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from .. import models, schemas, auth
from ..database import get_db
from datetime import datetime

router = APIRouter(
    prefix="/api/orders",
    tags=["orders"]
)

@router.get("/", response_model=List[schemas.Order])
async def get_orders(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
    skip: int = 0,
    limit: int = 100
):
    """Get all orders for current user (or all orders for admin)"""
    query = select(models.Order)
    if not auth.is_admin(current_user):
        query = query.filter(models.Order.user_id == current_user.id)
    
    result = await db.execute(
        query.offset(skip).limit(limit)
    )
    orders = result.scalars().all()
    return orders

@router.post("/", response_model=schemas.Order)
async def create_order(
    order: schemas.OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Create a new order"""
    # Calculate total amount and create order
    total_amount = 0
    order_items = []
    
    for item in order.items:
        # Get product price
        result = await db.execute(
            select(models.Product).filter(models.Product.id == item.product_id)
        )
        product = result.scalar_one_or_none()
        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product {item.product_id} not found"
            )
        if not product.available:
            raise HTTPException(
                status_code=400,
                detail=f"Product {product.name} is not available"
            )
        
        # Calculate item total
        item_total = product.price * item.quantity
        total_amount += item_total
        
        # Create order item
        order_items.append(models.OrderItem(
            product_id=product.id,
            quantity=item.quantity,
            unit_price=product.price
        ))
    
    # Create the order
    db_order = models.Order(
        user_id=current_user.id,
        status=models.OrderStatus.PENDING.value,
        total_amount=total_amount,
        items=order_items
    )
    
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)
    return db_order

@router.get("/{order_id}", response_model=schemas.Order)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get a specific order"""
    result = await db.execute(
        select(models.Order).filter(models.Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if not auth.is_admin(current_user) and order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this order")
    
    return order

@router.put("/{order_id}/status", response_model=schemas.Order)
async def update_order_status(
    order_id: int,
    status: models.OrderStatus,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_admin_user)
):
    """Update order status (admin only)"""
    result = await db.execute(
        select(models.Order).filter(models.Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = status.value
    order.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(order)
    return order
