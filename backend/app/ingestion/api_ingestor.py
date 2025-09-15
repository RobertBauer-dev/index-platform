"""
API data ingestion (Alpha Vantage, Yahoo Finance, etc.)
"""
import pandas as pd
import requests
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime, timedelta
import time

from app.ingestion.base import DataSource, DataIngestionManager
from app.core.config import settings


class AlphaVantageDataSource(DataSource):
    """Alpha Vantage API data source"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.ALPHA_VANTAGE_API_KEY
        self.base_url = "https://www.alphavantage.co/query"
        self.logger = logging.getLogger(__name__)
    
    def extract(self, symbol: str, function: str = "TIME_SERIES_DAILY", **kwargs) -> pd.DataFrame:
        """Extract data from Alpha Vantage API"""
        params = {
            'function': function,
            'symbol': symbol,
            'apikey': self.api_key,
            'outputsize': kwargs.get('outputsize', 'full'),
            'datatype': 'json'
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Check for API errors
            if 'Error Message' in data:
                raise Exception(f"Alpha Vantage API Error: {data['Error Message']}")
            
            if 'Note' in data:
                raise Exception(f"Alpha Vantage API Limit: {data['Note']}")
            
            # Extract time series data
            if function == "TIME_SERIES_DAILY":
                time_series_key = "Time Series (Daily)"
            elif function == "TIME_SERIES_WEEKLY":
                time_series_key = "Weekly Time Series"
            elif function == "TIME_SERIES_MONTHLY":
                time_series_key = "Monthly Time Series"
            else:
                raise ValueError(f"Unsupported function: {function}")
            
            if time_series_key not in data:
                raise Exception(f"No time series data found for {symbol}")
            
            # Convert to DataFrame
            time_series = data[time_series_key]
            df_data = []
            
            for date_str, values in time_series.items():
                df_data.append({
                    'symbol': symbol,
                    'date': datetime.strptime(date_str, '%Y-%m-%d'),
                    'open_price': float(values['1. open']),
                    'high_price': float(values['2. high']),
                    'low_price': float(values['3. low']),
                    'close_price': float(values['4. close']),
                    'volume': int(values['5. volume'])
                })
            
            df = pd.DataFrame(df_data)
            df = df.sort_values('date')
            
            return df
            
        except requests.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Error extracting data from Alpha Vantage: {str(e)}")
    
    def validate(self, data: pd.DataFrame) -> bool:
        """Validate Alpha Vantage data"""
        if data.empty:
            raise ValueError("No data received from Alpha Vantage")
        
        required_columns = ['symbol', 'date', 'close_price']
        missing_columns = set(required_columns) - set(data.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        return True


class YahooFinanceDataSource(DataSource):
    """Yahoo Finance API data source"""
    
    def __init__(self):
        self.base_url = settings.YAHOO_FINANCE_API_URL
        self.logger = logging.getLogger(__name__)
    
    def extract(self, symbol: str, start_date: str = None, end_date: str = None, **kwargs) -> pd.DataFrame:
        """Extract data from Yahoo Finance API"""
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        # Convert dates to timestamps
        start_timestamp = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
        end_timestamp = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())
        
        url = f"{self.base_url}/v8/finance/chart/{symbol}"
        params = {
            'period1': start_timestamp,
            'period2': end_timestamp,
            'interval': kwargs.get('interval', '1d'),
            'includePrePost': 'true',
            'events': 'div,split'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'chart' not in data or not data['chart']['result']:
                raise Exception(f"No data found for symbol: {symbol}")
            
            result = data['chart']['result'][0]
            timestamps = result['timestamp']
            quotes = result['indicators']['quote'][0]
            
            # Convert to DataFrame
            df_data = []
            for i, timestamp in enumerate(timestamps):
                df_data.append({
                    'symbol': symbol,
                    'date': datetime.fromtimestamp(timestamp),
                    'open_price': quotes['open'][i],
                    'high_price': quotes['high'][i],
                    'low_price': quotes['low'][i],
                    'close_price': quotes['close'][i],
                    'volume': quotes['volume'][i]
                })
            
            df = pd.DataFrame(df_data)
            df = df.dropna()  # Remove rows with NaN values
            df = df.sort_values('date')
            
            return df
            
        except requests.RequestException as e:
            raise Exception(f"Yahoo Finance API request failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Error extracting data from Yahoo Finance: {str(e)}")
    
    def validate(self, data: pd.DataFrame) -> bool:
        """Validate Yahoo Finance data"""
        if data.empty:
            raise ValueError("No data received from Yahoo Finance")
        
        required_columns = ['symbol', 'date', 'close_price']
        missing_columns = set(required_columns) - set(data.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        return True


class APIIngestor:
    """API data ingestor"""
    
    def __init__(self, db_session):
        self.db_session = db_session
        self.ingestion_manager = DataIngestionManager(db_session)
        self.logger = logging.getLogger(__name__)
    
    def ingest_from_alpha_vantage(self, symbols: List[str], function: str = "TIME_SERIES_DAILY") -> Dict[str, Any]:
        """Ingest data from Alpha Vantage for multiple symbols"""
        if not settings.ALPHA_VANTAGE_API_KEY:
            return {"error": "Alpha Vantage API key not configured"}
        
        results = {}
        alpha_vantage = AlphaVantageDataSource()
        
        for symbol in symbols:
            try:
                # Rate limiting - Alpha Vantage has 5 calls per minute limit
                time.sleep(12)  # Wait 12 seconds between calls
                
                # Extract data
                data = alpha_vantage.extract(symbol, function)
                
                # Validate data
                alpha_vantage.validate(data)
                
                # Ingest data
                result = self.ingestion_manager.ingest_prices(data)
                results[symbol] = result
                
            except Exception as e:
                self.logger.error(f"Error ingesting {symbol} from Alpha Vantage: {str(e)}")
                results[symbol] = {"error": str(e)}
        
        return results
    
    def ingest_from_yahoo_finance(self, symbols: List[str], start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Ingest data from Yahoo Finance for multiple symbols"""
        results = {}
        yahoo_finance = YahooFinanceDataSource()
        
        for symbol in symbols:
            try:
                # Extract data
                data = yahoo_finance.extract(symbol, start_date, end_date)
                
                # Validate data
                yahoo_finance.validate(data)
                
                # Ingest data
                result = self.ingestion_manager.ingest_prices(data)
                results[symbol] = result
                
            except Exception as e:
                self.logger.error(f"Error ingesting {symbol} from Yahoo Finance: {str(e)}")
                results[symbol] = {"error": str(e)}
        
        return results
    
    def ingest_securities_from_api(self, symbols: List[str], source: str = "yahoo") -> Dict[str, Any]:
        """Ingest security master data from API"""
        results = {}
        
        for symbol in symbols:
            try:
                # Get basic security info (this would need to be implemented based on available APIs)
                # For now, we'll create basic security records
                from app.db import models
                
                existing_security = self.db_session.query(models.Security).filter(
                    models.Security.symbol == symbol
                ).first()
                
                if not existing_security:
                    security_data = {
                        'symbol': symbol,
                        'name': symbol,  # Would need to fetch from API
                        'currency': 'USD',
                        'is_active': True
                    }
                    
                    new_security = models.Security(**security_data)
                    self.db_session.add(new_security)
                    self.db_session.commit()
                    
                    results[symbol] = {"created": True}
                else:
                    results[symbol] = {"exists": True}
                    
            except Exception as e:
                self.logger.error(f"Error creating security {symbol}: {str(e)}")
                results[symbol] = {"error": str(e)}
        
        return results
