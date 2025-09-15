"""
Pydantic schemas for API serialization
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# Security schemas
class SecurityBase(BaseModel):
    symbol: str
    name: str
    exchange: Optional[str] = None
    currency: str = "USD"
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    market_cap: Optional[float] = None
    is_active: bool = True


class SecurityCreate(SecurityBase):
    pass


class SecurityUpdate(BaseModel):
    name: Optional[str] = None
    exchange: Optional[str] = None
    currency: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    market_cap: Optional[float] = None
    is_active: Optional[bool] = None


class Security(SecurityBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Price Data schemas
class PriceDataBase(BaseModel):
    date: datetime
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    close_price: float
    volume: Optional[float] = None
    adjusted_close: Optional[float] = None
    dividend: float = 0.0
    split_ratio: float = 1.0


class PriceDataCreate(PriceDataBase):
    security_id: int


class PriceDataUpdate(BaseModel):
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    close_price: Optional[float] = None
    volume: Optional[float] = None
    adjusted_close: Optional[float] = None
    dividend: Optional[float] = None
    split_ratio: Optional[float] = None


class PriceData(PriceDataBase):
    id: int
    security_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Index Definition schemas
class IndexDefinitionBase(BaseModel):
    name: str
    description: Optional[str] = None
    weighting_method: str
    rebalance_frequency: str = "monthly"
    max_constituents: Optional[int] = None
    min_market_cap: Optional[float] = None
    max_market_cap: Optional[float] = None
    sectors: Optional[str] = None
    countries: Optional[str] = None
    esg_criteria: Optional[str] = None
    is_active: bool = True


class IndexDefinitionCreate(IndexDefinitionBase):
    pass


class IndexDefinitionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    weighting_method: Optional[str] = None
    rebalance_frequency: Optional[str] = None
    max_constituents: Optional[int] = None
    min_market_cap: Optional[float] = None
    max_market_cap: Optional[float] = None
    sectors: Optional[str] = None
    countries: Optional[str] = None
    esg_criteria: Optional[str] = None
    is_active: Optional[bool] = None


class IndexDefinition(IndexDefinitionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Index Value schemas
class IndexValueBase(BaseModel):
    date: datetime
    index_value: float
    total_return: Optional[float] = None
    price_return: Optional[float] = None
    dividend_yield: Optional[float] = None
    volatility: Optional[float] = None
    sharpe_ratio: Optional[float] = None


class IndexValueCreate(IndexValueBase):
    index_definition_id: int


class IndexValue(IndexValueBase):
    id: int
    index_definition_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Index Constituent schemas
class IndexConstituentBase(BaseModel):
    date: datetime
    weight: float
    shares: Optional[float] = None
    market_cap: Optional[float] = None
    is_new_addition: bool = False
    is_removal: bool = False


class IndexConstituentCreate(IndexConstituentBase):
    index_definition_id: int
    security_id: int


class IndexConstituent(IndexConstituentBase):
    id: int
    index_definition_id: int
    security_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# User schemas
class UserBase(BaseModel):
    email: str
    username: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Custom Index schemas
class CustomIndexBase(BaseModel):
    name: str
    description: Optional[str] = None
    filters: str  # JSON string
    weighting_method: str
    start_date: datetime
    end_date: Optional[datetime] = None
    is_public: bool = False


class CustomIndexCreate(CustomIndexBase):
    pass


class CustomIndexUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    filters: Optional[str] = None
    weighting_method: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_public: Optional[bool] = None


class CustomIndex(CustomIndexBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Backtest Result schemas
class BacktestResultBase(BaseModel):
    date: datetime
    index_value: float
    total_return: Optional[float] = None
    price_return: Optional[float] = None
    volatility: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None


class BacktestResultCreate(BacktestResultBase):
    custom_index_id: int


class BacktestResult(BacktestResultBase):
    id: int
    custom_index_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# API Response schemas
class IndexPerformance(BaseModel):
    """Index performance summary"""
    index_id: int
    index_name: str
    current_value: float
    total_return_1d: Optional[float] = None
    total_return_1w: Optional[float] = None
    total_return_1m: Optional[float] = None
    total_return_3m: Optional[float] = None
    total_return_1y: Optional[float] = None
    volatility: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None


class IndexConstituentWithSecurity(BaseModel):
    """Index constituent with security details"""
    constituent: IndexConstituent
    security: Security
    
    class Config:
        from_attributes = True


class CustomIndexBuilderRequest(BaseModel):
    """Request for building a custom index"""
    name: str
    description: Optional[str] = None
    filters: Dict[str, Any]
    weighting_method: str
    start_date: datetime
    end_date: Optional[datetime] = None


class CustomIndexBuilderResponse(BaseModel):
    """Response from custom index builder"""
    custom_index_id: int
    backtest_results: List[BacktestResult]
    performance_metrics: Dict[str, float]
