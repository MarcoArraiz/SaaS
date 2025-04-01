from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(
    prefix="/api/products",
    tags=["products"]
)

@router.get("/", response_model=List[schemas.Product])
async def get_products(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Get all products"""
    result = await db.execute(
        select(models.Product)
        .offset(skip)
        .limit(limit)
    )
    products = result.scalars().all()
    return products

@router.post("/", response_model=schemas.Product)
async def create_product(
    product: schemas.ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_admin_user)
):
    """Create a new product (admin only)"""
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product

@router.get("/{product_id}", response_model=schemas.Product)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific product by ID"""
    result = await db.execute(
        select(models.Product).filter(models.Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=schemas.Product)
async def update_product(
    product_id: int,
    product_update: schemas.ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_admin_user)
):
    """Update a product (admin only)"""
    result = await db.execute(
        select(models.Product).filter(models.Product.id == product_id)
    )
    db_product = result.scalar_one_or_none()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    for key, value in product_update.model_dump().items():
        setattr(db_product, key, value)
    
    await db.commit()
    await db.refresh(db_product)
    return db_product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_admin_user)
):
    """Delete a product (admin only)"""
    result = await db.execute(
        select(models.Product).filter(models.Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    await db.delete(product)
    await db.commit()
    return None
