"""
Users API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.db import models, schemas
from app.api.api_v1.deps import get_current_user, get_current_superuser

router = APIRouter()


@router.get("/me", response_model=schemas.User)
async def get_current_user_info(current_user: models.User = Depends(get_current_user)):
    """Get current user information"""
    return current_user


@router.put("/me", response_model=schemas.User)
async def update_current_user(
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    update_data = user_update.dict(exclude_unset=True)
    
    # Don't allow updating is_superuser field
    if 'is_superuser' in update_data:
        del update_data['is_superuser']
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.get("/", response_model=List[schemas.User])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_superuser)
):
    """Get list of users (admin only)"""
    query = db.query(models.User)
    
    if is_active is not None:
        query = query.filter(models.User.is_active == is_active)
    
    users = query.offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=schemas.User)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_superuser)
):
    """Get user by ID (admin only)"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=schemas.User)
async def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_superuser)
):
    """Create new user (admin only)"""
    # Check if user already exists
    existing_user = db.query(models.User).filter(
        (models.User.email == user.email) | (models.User.username == user.username)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email or username already exists")
    
    # Hash password
    from app.core.security import get_password_hash
    hashed_password = get_password_hash(user.password)
    
    db_user = models.User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=hashed_password,
        is_active=user.is_active,
        is_superuser=user.is_superuser
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.put("/{user_id}", response_model=schemas.User)
async def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_superuser)
):
    """Update user (admin only)"""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_update.dict(exclude_unset=True)
    
    # Hash password if provided
    if 'password' in update_data:
        from app.core.security import get_password_hash
        update_data['hashed_password'] = get_password_hash(update_data.pop('password'))
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_superuser)
):
    """Delete user (admin only)"""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    
    return {"message": "User deleted successfully"}


@router.get("/me/custom-indices", response_model=List[schemas.CustomIndex])
async def get_user_custom_indices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's custom indices"""
    custom_indices = db.query(models.CustomIndex).filter(
        models.CustomIndex.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return custom_indices


@router.get("/{user_id}/custom-indices", response_model=List[schemas.CustomIndex])
async def get_user_custom_indices_admin(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: models.User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """Get user's custom indices (admin only)"""
    custom_indices = db.query(models.CustomIndex).filter(
        models.CustomIndex.user_id == user_id
    ).offset(skip).limit(limit).all()
    
    return custom_indices
