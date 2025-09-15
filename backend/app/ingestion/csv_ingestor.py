"""
CSV data ingestion
"""
import pandas as pd
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging

from app.ingestion.base import DataSource, DataIngestionManager
from app.db import schemas


class CSVDataSource(DataSource):
    """CSV file data source"""
    
    def __init__(self, file_path: str, encoding: str = 'utf-8'):
        self.file_path = Path(file_path)
        self.encoding = encoding
    
    def extract(self, **kwargs) -> pd.DataFrame:
        """Extract data from CSV file"""
        try:
            # Try different separators
            for sep in [',', ';', '\t']:
                try:
                    df = pd.read_csv(self.file_path, encoding=self.encoding, sep=sep)
                    if len(df.columns) > 1:  # Valid separator found
                        break
                except:
                    continue
            else:
                raise ValueError(f"Could not parse CSV file: {self.file_path}")
            
            return df
        except Exception as e:
            raise Exception(f"Error reading CSV file {self.file_path}: {str(e)}")
    
    def validate(self, data: pd.DataFrame) -> bool:
        """Validate CSV data"""
        if data.empty:
            raise ValueError("CSV file is empty")
        
        # Check for required columns based on data type
        required_columns = {
            'securities': ['symbol', 'name'],
            'prices': ['symbol', 'date', 'close_price']
        }
        
        # Determine data type based on columns
        data_type = None
        if 'symbol' in data.columns and 'name' in data.columns:
            data_type = 'securities'
        elif 'symbol' in data.columns and 'date' in data.columns and 'close_price' in data.columns:
            data_type = 'prices'
        
        if data_type and data_type in required_columns:
            missing_columns = set(required_columns[data_type]) - set(data.columns)
            if missing_columns:
                raise ValueError(f"Missing required columns for {data_type}: {missing_columns}")
        
        return True


class CSVIngestor:
    """CSV data ingestor"""
    
    def __init__(self, db_session, file_path: str):
        self.db_session = db_session
        self.file_path = file_path
        self.data_source = CSVDataSource(file_path)
        self.ingestion_manager = DataIngestionManager(db_session)
        self.logger = logging.getLogger(__name__)
    
    def ingest_securities_from_csv(self, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Ingest securities from CSV file"""
        csv_path = file_path or self.file_path
        
        try:
            # Extract data
            data = self.data_source.extract()
            
            # Validate data
            self.data_source.validate(data)
            
            # Determine if this is securities data
            if 'symbol' in data.columns and 'name' in data.columns:
                return self.ingestion_manager.ingest_securities(data)
            else:
                return {"error": "CSV does not contain securities data"}
                
        except Exception as e:
            self.logger.error(f"Error ingesting securities from CSV: {str(e)}")
            return {"error": str(e)}
    
    def ingest_prices_from_csv(self, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Ingest price data from CSV file"""
        csv_path = file_path or self.file_path
        
        try:
            # Extract data
            data = self.data_source.extract()
            
            # Validate data
            self.data_source.validate(data)
            
            # Determine if this is price data
            if 'symbol' in data.columns and 'date' in data.columns and 'close_price' in data.columns:
                return self.ingestion_manager.ingest_prices(data)
            else:
                return {"error": "CSV does not contain price data"}
                
        except Exception as e:
            self.logger.error(f"Error ingesting prices from CSV: {str(e)}")
            return {"error": str(e)}
    
    def ingest_multiple_files(self, file_paths: List[str], data_types: List[str]) -> Dict[str, Any]:
        """Ingest multiple CSV files"""
        results = {}
        
        for file_path, data_type in zip(file_paths, data_types):
            try:
                csv_ingestor = CSVIngestor(self.db_session, file_path)
                
                if data_type == 'securities':
                    results[file_path] = csv_ingestor.ingest_securities_from_csv()
                elif data_type == 'prices':
                    results[file_path] = csv_ingestor.ingest_prices_from_csv()
                else:
                    results[file_path] = {"error": f"Unknown data type: {data_type}"}
                    
            except Exception as e:
                results[file_path] = {"error": str(e)}
        
        return results
    
    def get_csv_template(self, data_type: str) -> Dict[str, Any]:
        """Get CSV template for data type"""
        templates = {
            'securities': {
                'columns': ['symbol', 'name', 'exchange', 'currency', 'sector', 'industry', 'country', 'market_cap'],
                'sample_data': {
                    'symbol': ['AAPL', 'MSFT', 'GOOGL'],
                    'name': ['Apple Inc.', 'Microsoft Corporation', 'Alphabet Inc.'],
                    'exchange': ['NASDAQ', 'NASDAQ', 'NASDAQ'],
                    'currency': ['USD', 'USD', 'USD'],
                    'sector': ['Technology', 'Technology', 'Technology'],
                    'industry': ['Consumer Electronics', 'Software', 'Internet Services'],
                    'country': ['USA', 'USA', 'USA'],
                    'market_cap': [3000000000000, 2500000000000, 1800000000000]
                }
            },
            'prices': {
                'columns': ['symbol', 'date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume'],
                'sample_data': {
                    'symbol': ['AAPL', 'AAPL', 'AAPL'],
                    'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
                    'open_price': [190.0, 192.0, 191.0],
                    'high_price': [195.0, 194.0, 193.0],
                    'low_price': [189.0, 191.0, 190.0],
                    'close_price': [192.0, 191.0, 192.5],
                    'volume': [1000000, 1200000, 1100000]
                }
            }
        }
        
        return templates.get(data_type, {})
