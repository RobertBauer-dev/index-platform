"""
Price data API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.db import models, schemas

router = APIRouter()


@router.get("/", response_model=List[schemas.PriceData])
async def get_prices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    symbol: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get price data with optional filters"""
    query = db.query(models.PriceData)
    
    if symbol:
        # Join with securities table to filter by symbol
        query = query.join(models.Security).filter(models.Security.symbol == symbol)
    
    if start_date:
        query = query.filter(models.PriceData.date >= start_date)
    
    if end_date:
        query = query.filter(models.PriceData.date <= end_date)
    
    prices = query.order_by(models.PriceData.date.desc()).offset(skip).limit(limit).all()
    return prices


@router.get("/{price_id}", response_model=schemas.PriceData)
async def get_price(price_id: int, db: Session = Depends(get_db)):
    """Get price data by ID"""
    price = db.query(models.PriceData).filter(models.PriceData.id == price_id).first()
    if not price:
        raise HTTPException(status_code=404, detail="Price data not found")
    return price


@router.post("/", response_model=schemas.PriceData)
async def create_price(
    price: schemas.PriceDataCreate,
    db: Session = Depends(get_db)
):
    """Create new price data"""
    db_price = models.PriceData(**price.dict())
    db.add(db_price)
    db.commit()
    db.refresh(db_price)
    
    return db_price


@router.post("/bulk", response_model=dict)
async def create_prices_bulk(
    prices: List[schemas.PriceDataCreate],
    db: Session = Depends(get_db)
):
    """Create multiple price data entries"""
    created_count = 0
    errors = []
    
    for price_data in prices:
        try:
            db_price = models.PriceData(**price_data.dict())
            db.add(db_price)
            created_count += 1
        except Exception as e:
            errors.append(f"Error creating price data: {str(e)}")
    
    db.commit()
    
    return {
        "created": created_count,
        "errors": errors,
        "total_processed": len(prices)
    }


@router.put("/{price_id}", response_model=schemas.PriceData)
async def update_price(
    price_id: int,
    price_update: schemas.PriceDataUpdate,
    db: Session = Depends(get_db)
):
    """Update price data"""
    db_price = db.query(models.PriceData).filter(models.PriceData.id == price_id).first()
    if not db_price:
        raise HTTPException(status_code=404, detail="Price data not found")
    
    update_data = price_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_price, field, value)
    
    db.commit()
    db.refresh(db_price)
    
    return db_price


@router.delete("/{price_id}")
async def delete_price(
    price_id: int,
    db: Session = Depends(get_db)
):
    """Delete price data"""
    db_price = db.query(models.PriceData).filter(models.PriceData.id == price_id).first()
    if not db_price:
        raise HTTPException(status_code=404, detail="Price data not found")
    
    db.delete(db_price)
    db.commit()
    
    return {"message": "Price data deleted successfully"}


@router.get("/latest/{symbol}")
async def get_latest_price(
    symbol: str,
    db: Session = Depends(get_db)
):
    """Get latest price for a symbol"""
    # Get security by symbol
    security = db.query(models.Security).filter(models.Security.symbol == symbol).first()
    if not security:
        raise HTTPException(status_code=404, detail="Security not found")
    
    # Get latest price
    latest_price = db.query(models.PriceData).filter(
        models.PriceData.security_id == security.id
    ).order_by(models.PriceData.date.desc()).first()
    
    if not latest_price:
        raise HTTPException(status_code=404, detail="No price data found for this security")
    
    return {
        "symbol": symbol,
        "security_name": security.name,
        "latest_price": latest_price.close_price,
        "date": latest_price.date,
        "volume": latest_price.volume,
        "change": None,  # Would need to calculate from previous day
        "change_percent": None
    }


@router.get("/symbol/{symbol}/history")
async def get_price_history(
    symbol: str,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get price history for a symbol"""
    # Get security by symbol
    security = db.query(models.Security).filter(models.Security.symbol == symbol).first()
    if not security:
        raise HTTPException(status_code=404, detail="Security not found")
    
    # Get price history
    query = db.query(models.PriceData).filter(models.PriceData.security_id == security.id)
    
    if start_date:
        query = query.filter(models.PriceData.date >= start_date)
    if end_date:
        query = query.filter(models.PriceData.date <= end_date)
    
    prices = query.order_by(models.PriceData.date.desc()).limit(limit).all()
    
    # Format response
    price_history = []
    for price in prices:
        price_history.append({
            "date": price.date,
            "open": price.open_price,
            "high": price.high_price,
            "low": price.low_price,
            "close": price.close_price,
            "volume": price.volume,
            "adjusted_close": price.adjusted_close
        })
    
    return {
        "symbol": symbol,
        "security_name": security.name,
        "price_history": price_history
    }


@router.get("/symbols/latest")
async def get_latest_prices(
    symbols: List[str] = Query(...),
    db: Session = Depends(get_db)
):
    """Get latest prices for multiple symbols"""
    # Get securities
    securities = db.query(models.Security).filter(
        models.Security.symbol.in_(symbols)
    ).all()
    
    security_map = {s.symbol: s for s in securities}
    
    results = []
    for symbol in symbols:
        if symbol not in security_map:
            results.append({
                "symbol": symbol,
                "error": "Security not found"
            })
            continue
        
        security = security_map[symbol]
        
        # Get latest price
        latest_price = db.query(models.PriceData).filter(
            models.PriceData.security_id == security.id
        ).order_by(models.PriceData.date.desc()).first()
        
        if latest_price:
            results.append({
                "symbol": symbol,
                "security_name": security.name,
                "latest_price": latest_price.close_price,
                "date": latest_price.date,
                "volume": latest_price.volume
            })
        else:
            results.append({
                "symbol": symbol,
                "error": "No price data available"
            })
    
    return {"prices": results}
