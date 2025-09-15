"""
Base classes for data ingestion
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import pandas as pd
from sqlalchemy.orm import Session

from app.db.schemas import SecurityCreate, PriceDataCreate


class DataSource(ABC):
    """Abstract base class for data sources"""
    
    @abstractmethod
    def extract(self, **kwargs) -> pd.DataFrame:
        """Extract data from source"""
        pass
    
    @abstractmethod
    def validate(self, data: pd.DataFrame) -> bool:
        """Validate extracted data"""
        pass


class DataIngestor(ABC):
    """Abstract base class for data ingestion"""
    
    def __init__(self, db: Session):
        self.db = db
    
    @abstractmethod
    def ingest(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Ingest data into database"""
        pass
    
    @abstractmethod
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform raw data"""
        pass


class SecurityIngestor(DataIngestor):
    """Ingest security master data"""
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform security data"""
        # Clean column names
        data.columns = data.columns.str.lower().str.replace(' ', '_')
        
        # Handle missing values
        data = data.fillna('')
        
        # Convert market cap to float if it's a string
        if 'market_cap' in data.columns:
            data['market_cap'] = pd.to_numeric(data['market_cap'], errors='coerce')
        
        return data
    
    def ingest(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Ingest security data"""
        from app.db import models
        
        transformed_data = self.transform(data)
        
        created_count = 0
        updated_count = 0
        errors = []
        
        for _, row in transformed_data.iterrows():
            try:
                # Check if security exists
                existing_security = self.db.query(models.Security).filter(
                    models.Security.symbol == row['symbol']
                ).first()
                
                if existing_security:
                    # Update existing
                    for key, value in row.items():
                        if hasattr(existing_security, key) and value is not None:
                            setattr(existing_security, key, value)
                    updated_count += 1
                else:
                    # Create new
                    security_data = SecurityCreate(**row.to_dict())
                    new_security = models.Security(**security_data.dict())
                    self.db.add(new_security)
                    created_count += 1
                    
            except Exception as e:
                errors.append(f"Error processing {row.get('symbol', 'unknown')}: {str(e)}")
        
        self.db.commit()
        
        return {
            "created": created_count,
            "updated": updated_count,
            "errors": errors
        }


class PriceDataIngestor(DataIngestor):
    """Ingest price data"""
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform price data"""
        # Clean column names
        data.columns = data.columns.str.lower().str.replace(' ', '_')
        
        # Convert date column
        if 'date' in data.columns:
            data['date'] = pd.to_datetime(data['date'])
        
        # Convert numeric columns
        numeric_columns = ['open_price', 'high_price', 'low_price', 'close_price', 'volume', 'adjusted_close']
        for col in numeric_columns:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce')
        
        # Fill missing values
        data = data.fillna(0)
        
        return data
    
    def ingest(self, data: pd.DataFrame, security_id: Optional[int] = None) -> Dict[str, Any]:
        """Ingest price data"""
        from app.db import models
        
        transformed_data = self.transform(data)
        
        created_count = 0
        errors = []
        
        for _, row in transformed_data.iterrows():
            try:
                # Get security_id if not provided
                if security_id is None:
                    if 'symbol' in row:
                        security = self.db.query(models.Security).filter(
                            models.Security.symbol == row['symbol']
                        ).first()
                        if not security:
                            errors.append(f"Security not found: {row['symbol']}")
                            continue
                        security_id = security.id
                    else:
                        errors.append("No security_id or symbol provided")
                        continue
                
                # Check if price data already exists
                existing_price = self.db.query(models.PriceData).filter(
                    models.PriceData.security_id == security_id,
                    models.PriceData.date == row['date']
                ).first()
                
                if not existing_price:
                    # Create new price data
                    price_data_dict = row.to_dict()
                    price_data_dict['security_id'] = security_id
                    price_data = PriceDataCreate(**price_data_dict)
                    new_price_data = models.PriceData(**price_data.dict())
                    self.db.add(new_price_data)
                    created_count += 1
                    
            except Exception as e:
                errors.append(f"Error processing price data for date {row.get('date', 'unknown')}: {str(e)}")
        
        self.db.commit()
        
        return {
            "created": created_count,
            "errors": errors
        }


class DataIngestionManager:
    """Manager for data ingestion operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.security_ingestor = SecurityIngestor(db)
        self.price_ingestor = PriceDataIngestor(db)
    
    def ingest_securities(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Ingest security data"""
        return self.security_ingestor.ingest(data)
    
    def ingest_prices(self, data: pd.DataFrame, security_id: Optional[int] = None) -> Dict[str, Any]:
        """Ingest price data"""
        return self.price_ingestor.ingest(data, security_id)
    
    def bulk_ingest(self, securities_data: pd.DataFrame, prices_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Bulk ingest securities and their price data"""
        results = {
            "securities": self.ingest_securities(securities_data),
            "prices": {}
        }
        
        # Get security mapping
        securities = self.db.query(models.Security).all()
        security_map = {s.symbol: s.id for s in securities}
        
        # Ingest price data for each security
        for symbol, price_data in prices_data.items():
            if symbol in security_map:
                results["prices"][symbol] = self.ingest_prices(price_data, security_map[symbol])
            else:
                results["prices"][symbol] = {"error": f"Security {symbol} not found"}
        
        return results
