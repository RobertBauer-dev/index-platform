"""
Indices API endpoints
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.db import models, schemas
from app.api.api_v1.deps import get_current_user
from app.calculation.index_engine import IndexEngine

router = APIRouter()


@router.get("/", response_model=List[schemas.IndexDefinition])
async def get_indices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """Get list of index definitions"""
    query = db.query(models.IndexDefinition)
    
    if is_active is not None:
        query = query.filter(models.IndexDefinition.is_active == is_active)
    
    indices = query.offset(skip).limit(limit).all()
    return indices


@router.get("/{index_id}", response_model=schemas.IndexDefinition)
async def get_index(index_id: int, db: Session = Depends(get_db)):
    """Get index definition by ID"""
    index = db.query(models.IndexDefinition).filter(models.IndexDefinition.id == index_id).first()
    if not index:
        raise HTTPException(status_code=404, detail="Index not found")
    return index


@router.post("/", response_model=schemas.IndexDefinition)
async def create_index(
    index: schemas.IndexDefinitionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Create new index definition"""
    # Check if index already exists
    existing_index = db.query(models.IndexDefinition).filter(
        models.IndexDefinition.name == index.name
    ).first()
    
    if existing_index:
        raise HTTPException(status_code=400, detail="Index with this name already exists")
    
    db_index = models.IndexDefinition(**index.dict())
    db.add(db_index)
    db.commit()
    db.refresh(db_index)
    
    return db_index


@router.put("/{index_id}", response_model=schemas.IndexDefinition)
async def update_index(
    index_id: int,
    index_update: schemas.IndexDefinitionUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Update index definition"""
    db_index = db.query(models.IndexDefinition).filter(models.IndexDefinition.id == index_id).first()
    if not db_index:
        raise HTTPException(status_code=404, detail="Index not found")
    
    update_data = index_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_index, field, value)
    
    db.commit()
    db.refresh(db_index)
    
    return db_index


@router.delete("/{index_id}")
async def delete_index(
    index_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete index definition"""
    db_index = db.query(models.IndexDefinition).filter(models.IndexDefinition.id == index_id).first()
    if not db_index:
        raise HTTPException(status_code=404, detail="Index not found")
    
    db.delete(db_index)
    db.commit()
    
    return {"message": "Index deleted successfully"}


@router.get("/{index_id}/values", response_model=List[schemas.IndexValue])
async def get_index_values(
    index_id: int,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get index values for a date range"""
    query = db.query(models.IndexValue).filter(models.IndexValue.index_definition_id == index_id)
    
    if start_date:
        query = query.filter(models.IndexValue.date >= start_date)
    if end_date:
        query = query.filter(models.IndexValue.date <= end_date)
    
    values = query.order_by(models.IndexValue.date.desc()).limit(limit).all()
    return values


@router.get("/{index_id}/constituents", response_model=List[schemas.IndexConstituent])
async def get_index_constituents(
    index_id: int,
    date: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get index constituents for a specific date"""
    query = db.query(models.IndexConstituent).filter(
        models.IndexConstituent.index_definition_id == index_id,
        models.IndexConstituent.is_removal == False
    )
    
    if date:
        query = query.filter(models.IndexConstituent.date <= date)
    
    # Get latest constituents for each security
    constituents = query.order_by(
        models.IndexConstituent.date.desc()
    ).limit(limit).all()
    
    return constituents


@router.post("/{index_id}/calculate")
async def calculate_index(
    index_id: int,
    date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Calculate index value for a specific date"""
    index_engine = IndexEngine(db)
    
    calc_date = datetime.now()
    if date:
        try:
            calc_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")
    
    result = index_engine.calculate_index(index_id, calc_date)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.post("/{index_id}/rebalance")
async def rebalance_index(
    index_id: int,
    date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Rebalance index constituents"""
    index_engine = IndexEngine(db)
    
    rebalance_date = datetime.now()
    if date:
        try:
            rebalance_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")
    
    result = index_engine.rebalance_index(index_id, rebalance_date)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.post("/{index_id}/backtest")
async def backtest_index(
    index_id: int,
    start_date: str,
    end_date: Optional[str] = Query(None),
    rebalance_frequency: str = Query("monthly"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Backtest index performance"""
    index_engine = IndexEngine(db)
    
    try:
        start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid start_date format")
    
    end_dt = datetime.now()
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format")
    
    result = index_engine.backtest_index(index_id, start_dt, end_dt, rebalance_frequency)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.get("/{index_id}/performance", response_model=schemas.IndexPerformance)
async def get_index_performance(
    index_id: int,
    db: Session = Depends(get_db)
):
    """Get index performance summary"""
    # Get index definition
    index_def = db.query(models.IndexDefinition).filter(
        models.IndexDefinition.id == index_id
    ).first()
    
    if not index_def:
        raise HTTPException(status_code=404, detail="Index not found")
    
    # Get latest index value
    latest_value = db.query(models.IndexValue).filter(
        models.IndexValue.index_definition_id == index_id
    ).order_by(models.IndexValue.date.desc()).first()
    
    if not latest_value:
        raise HTTPException(status_code=404, detail="No index values found")
    
    # Calculate performance metrics
    index_engine = IndexEngine(db)
    performance_metrics = index_engine._calculate_performance_metrics(index_id, latest_value.date)
    
    return schemas.IndexPerformance(
        index_id=index_id,
        index_name=index_def.name,
        current_value=latest_value.index_value,
        total_return_1d=performance_metrics.get('total_return_1d'),
        total_return_1w=performance_metrics.get('total_return_1w'),
        total_return_1m=performance_metrics.get('total_return_1m'),
        total_return_3m=performance_metrics.get('total_return_3m'),
        total_return_1y=performance_metrics.get('total_return_1y'),
        volatility=performance_metrics.get('volatility'),
        sharpe_ratio=performance_metrics.get('sharpe_ratio'),
        max_drawdown=performance_metrics.get('max_drawdown')
    )


@router.post("/custom-index")
async def create_custom_index(
    index_request: schemas.CustomIndexBuilderRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Create and backtest a custom index"""
    # This would implement the custom index creation logic
    # For now, return a placeholder response
    return {
        "message": "Custom index creation not yet implemented",
        "request": index_request.dict()
    }
