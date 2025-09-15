"""
Database models for the Index Platform
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.core.database import Base


class Security(Base):
    """Security/Stock master data"""
    __tablename__ = "securities"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    exchange = Column(String(50))
    currency = Column(String(3), default="USD")
    sector = Column(String(100))
    industry = Column(String(100))
    country = Column(String(50))
    market_cap = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    price_data = relationship("PriceData", back_populates="security")
    index_constituents = relationship("IndexConstituent", back_populates="security")


class PriceData(Base):
    """Historical price data"""
    __tablename__ = "price_data"
    
    id = Column(Integer, primary_key=True, index=True)
    security_id = Column(Integer, ForeignKey("securities.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float, nullable=False)
    volume = Column(Float)
    adjusted_close = Column(Float)
    dividend = Column(Float, default=0.0)
    split_ratio = Column(Float, default=1.0)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    security = relationship("Security", back_populates="price_data")
    
    # Indexes
    __table_args__ = (
        Index('idx_price_data_security_date', 'security_id', 'date'),
        Index('idx_price_data_date', 'date'),
    )


class IndexDefinition(Base):
    """Index definitions and rules"""
    __tablename__ = "index_definitions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False)
    description = Column(Text)
    weighting_method = Column(String(50), nullable=False)  # equal_weight, market_cap_weight, etc.
    rebalance_frequency = Column(String(20), default="monthly")  # daily, weekly, monthly, quarterly
    max_constituents = Column(Integer)
    min_market_cap = Column(Float)
    max_market_cap = Column(Float)
    sectors = Column(Text)  # JSON string of allowed sectors
    countries = Column(Text)  # JSON string of allowed countries
    esg_criteria = Column(Text)  # JSON string of ESG filters
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    index_values = relationship("IndexValue", back_populates="index_definition")
    index_constituents = relationship("IndexConstituent", back_populates="index_definition")


class IndexValue(Base):
    """Historical index values"""
    __tablename__ = "index_values"
    
    id = Column(Integer, primary_key=True, index=True)
    index_definition_id = Column(Integer, ForeignKey("index_definitions.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    index_value = Column(Float, nullable=False)
    total_return = Column(Float)
    price_return = Column(Float)
    dividend_yield = Column(Float)
    volatility = Column(Float)
    sharpe_ratio = Column(Float)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    index_definition = relationship("IndexDefinition", back_populates="index_values")
    
    # Indexes
    __table_args__ = (
        Index('idx_index_values_index_date', 'index_definition_id', 'date'),
        Index('idx_index_values_date', 'date'),
    )


class IndexConstituent(Base):
    """Index constituents at specific dates"""
    __tablename__ = "index_constituents"
    
    id = Column(Integer, primary_key=True, index=True)
    index_definition_id = Column(Integer, ForeignKey("index_definitions.id"), nullable=False)
    security_id = Column(Integer, ForeignKey("securities.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    weight = Column(Float, nullable=False)
    shares = Column(Float)
    market_cap = Column(Float)
    is_new_addition = Column(Boolean, default=False)
    is_removal = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    index_definition = relationship("IndexDefinition", back_populates="index_constituents")
    security = relationship("Security", back_populates="index_constituents")
    
    # Indexes
    __table_args__ = (
        Index('idx_index_constituents_index_date', 'index_definition_id', 'date'),
        Index('idx_index_constituents_security_date', 'security_id', 'date'),
    )


class User(Base):
    """User accounts"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(200))
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    custom_indices = relationship("CustomIndex", back_populates="user")


class CustomIndex(Base):
    """User-created custom indices"""
    __tablename__ = "custom_indices"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    filters = Column(Text, nullable=False)  # JSON string of filter criteria
    weighting_method = Column(String(50), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="custom_indices")
    backtest_results = relationship("BacktestResult", back_populates="custom_index")


class BacktestResult(Base):
    """Backtest results for custom indices"""
    __tablename__ = "backtest_results"
    
    id = Column(Integer, primary_key=True, index=True)
    custom_index_id = Column(Integer, ForeignKey("custom_indices.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    index_value = Column(Float, nullable=False)
    total_return = Column(Float)
    price_return = Column(Float)
    volatility = Column(Float)
    sharpe_ratio = Column(Float)
    max_drawdown = Column(Float)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    custom_index = relationship("CustomIndex", back_populates="backtest_results")
    
    # Indexes
    __table_args__ = (
        Index('idx_backtest_results_index_date', 'custom_index_id', 'date'),
    )
