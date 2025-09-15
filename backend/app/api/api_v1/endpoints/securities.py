"""
Securities API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.db import models, schemas
from app.api.api_v1.deps import get_current_user

router = APIRouter()


@router.get("/", response_model=List[schemas.Security])
async def get_securities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    sector: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """Get list of securities"""
    query = db.query(models.Security)
    
    if search:
        query = query.filter(
            (models.Security.symbol.ilike(f"%{search}%")) |
            (models.Security.name.ilike(f"%{search}%"))
        )
    
    if sector:
        query = query.filter(models.Security.sector == sector)
    
    if country:
        query = query.filter(models.Security.country == country)
    
    if is_active is not None:
        query = query.filter(models.Security.is_active == is_active)
    
    securities = query.offset(skip).limit(limit).all()
    return securities


@router.get("/{security_id}", response_model=schemas.Security)
async def get_security(security_id: int, db: Session = Depends(get_db)):
    """Get security by ID"""
    security = db.query(models.Security).filter(models.Security.id == security_id).first()
    if not security:
        raise HTTPException(status_code=404, detail="Security not found")
    return security


@router.get("/symbol/{symbol}", response_model=schemas.Security)
async def get_security_by_symbol(symbol: str, db: Session = Depends(get_db)):
    """Get security by symbol"""
    security = db.query(models.Security).filter(models.Security.symbol == symbol).first()
    if not security:
        raise HTTPException(status_code=404, detail="Security not found")
    return security


@router.post("/", response_model=schemas.Security)
async def create_security(
    security: schemas.SecurityCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Create new security"""
    # Check if security already exists
    existing_security = db.query(models.Security).filter(
        models.Security.symbol == security.symbol
    ).first()
    
    if existing_security:
        raise HTTPException(status_code=400, detail="Security with this symbol already exists")
    
    db_security = models.Security(**security.dict())
    db.add(db_security)
    db.commit()
    db.refresh(db_security)
    
    return db_security


@router.put("/{security_id}", response_model=schemas.Security)
async def update_security(
    security_id: int,
    security_update: schemas.SecurityUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Update security"""
    db_security = db.query(models.Security).filter(models.Security.id == security_id).first()
    if not db_security:
        raise HTTPException(status_code=404, detail="Security not found")
    
    update_data = security_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_security, field, value)
    
    db.commit()
    db.refresh(db_security)
    
    return db_security


@router.delete("/{security_id}")
async def delete_security(
    security_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete security"""
    db_security = db.query(models.Security).filter(models.Security.id == security_id).first()
    if not db_security:
        raise HTTPException(status_code=404, detail="Security not found")
    
    db.delete(db_security)
    db.commit()
    
    return {"message": "Security deleted successfully"}


@router.get("/{security_id}/prices", response_model=List[schemas.PriceData])
async def get_security_prices(
    security_id: int,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get price data for a security"""
    query = db.query(models.PriceData).filter(models.PriceData.security_id == security_id)
    
    if start_date:
        query = query.filter(models.PriceData.date >= start_date)
    if end_date:
        query = query.filter(models.PriceData.date <= end_date)
    
    prices = query.order_by(models.PriceData.date.desc()).limit(limit).all()
    return prices


@router.get("/sectors/", response_model=List[str])
async def get_sectors(db: Session = Depends(get_db)):
    """Get list of available sectors"""
    sectors = db.query(models.Security.sector).distinct().filter(
        models.Security.sector.isnot(None),
        models.Security.sector != ""
    ).all()
    return [sector[0] for sector in sectors]


@router.get("/countries/", response_model=List[str])
async def get_countries(db: Session = Depends(get_db)):
    """Get list of available countries"""
    countries = db.query(models.Security.country).distinct().filter(
        models.Security.country.isnot(None),
        models.Security.country != ""
    ).all()
    return [country[0] for country in countries]
