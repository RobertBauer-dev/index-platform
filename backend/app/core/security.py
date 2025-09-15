"""
Security utilities
"""
from datetime import datetime, timedelta
from typing import Optional, Union
from jose import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.JWTError:
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str, db) -> Union[bool, dict]:
    """Authenticate user with username and password"""
    user = db.query(models.User).filter(models.User.username == username).first()
    
    if not user:
        return False
    
    if not verify_password(password, user.hashed_password):
        return False
    
    if not user.is_active:
        return False
    
    return user


def check_permissions(user: models.User, required_permission: str = None) -> bool:
    """Check if user has required permissions"""
    if not user.is_active:
        return False
    
    if user.is_superuser:
        return True
    
    # Add more permission logic here as needed
    return True
