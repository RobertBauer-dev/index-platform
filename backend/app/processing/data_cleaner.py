"""
Data cleaning and preprocessing
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging


class DataCleaner:
    """Data cleaning utilities"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def clean_price_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean price data"""
        original_count = len(df)
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['security_id', 'date'], keep='last')
        
        # Remove rows with missing close price
        df = df.dropna(subset=['close_price'])
        
        # Remove rows with negative prices
        df = df[df['close_price'] > 0]
        
        # Remove rows with extreme price changes (outliers)
        df = self._remove_price_outliers(df)
        
        # Fill missing values
        df = self._fill_missing_values(df)
        
        # Validate OHLC relationships
        df = self._validate_ohlc_relationships(df)
        
        cleaned_count = len(df)
        self.logger.info(f"Cleaned price data: {original_count} -> {cleaned_count} rows")
        
        return df
    
    def clean_security_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean security master data"""
        original_count = len(df)
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['symbol'], keep='last')
        
        # Remove rows with missing symbol or name
        df = df.dropna(subset=['symbol', 'name'])
        
        # Clean symbol format
        df['symbol'] = df['symbol'].str.upper().str.strip()
        
        # Clean name format
        df['name'] = df['name'].str.strip()
        
        # Standardize currency codes
        df = self._standardize_currencies(df)
        
        # Clean sector and industry data
        df = self._clean_sector_data(df)
        
        cleaned_count = len(df)
        self.logger.info(f"Cleaned security data: {original_count} -> {cleaned_count} rows")
        
        return df
    
    def _remove_price_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove extreme price outliers"""
        # Calculate daily returns
        df_sorted = df.sort_values(['security_id', 'date'])
        df_sorted['daily_return'] = df_sorted.groupby('security_id')['close_price'].pct_change()
        
        # Remove returns > 50% or < -50% (potential data errors)
        outlier_mask = (df_sorted['daily_return'] > 0.5) | (df_sorted['daily_return'] < -0.5)
        df_cleaned = df_sorted[~outlier_mask].drop('daily_return', axis=1)
        
        return df_cleaned
    
    def _fill_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fill missing values in price data"""
        # Forward fill for OHLC prices
        price_columns = ['open_price', 'high_price', 'low_price', 'close_price']
        for col in price_columns:
            if col in df.columns:
                df[col] = df.groupby('security_id')[col].fillna(method='ffill')
        
        # Fill volume with 0
        if 'volume' in df.columns:
            df['volume'] = df['volume'].fillna(0)
        
        # Fill dividend and split ratio
        df['dividend'] = df['dividend'].fillna(0)
        df['split_ratio'] = df['split_ratio'].fillna(1.0)
        
        return df
    
    def _validate_ohlc_relationships(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate OHLC price relationships"""
        # High should be >= max(open, close)
        if 'high_price' in df.columns and 'open_price' in df.columns and 'close_price' in df.columns:
            high_valid = df['high_price'] >= np.maximum(df['open_price'], df['close_price'])
            df = df[high_valid]
        
        # Low should be <= min(open, close)
        if 'low_price' in df.columns and 'open_price' in df.columns and 'close_price' in df.columns:
            low_valid = df['low_price'] <= np.minimum(df['open_price'], df['close_price'])
            df = df[low_valid]
        
        return df
    
    def _standardize_currencies(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize currency codes"""
        if 'currency' in df.columns:
            currency_mapping = {
                'US$': 'USD', '$': 'USD', 'US Dollar': 'USD',
                'EUR': 'EUR', '€': 'EUR', 'Euro': 'EUR',
                'GBP': 'GBP', '£': 'GBP', 'British Pound': 'GBP',
                'JPY': 'JPY', '¥': 'JPY', 'Japanese Yen': 'JPY',
                'CHF': 'CHF', 'Swiss Franc': 'CHF',
                'CAD': 'CAD', 'Canadian Dollar': 'CAD',
                'AUD': 'AUD', 'Australian Dollar': 'AUD'
            }
            
            df['currency'] = df['currency'].str.upper()
            df['currency'] = df['currency'].replace(currency_mapping)
            
            # Default to USD if currency is unknown
            df['currency'] = df['currency'].fillna('USD')
        
        return df
    
    def _clean_sector_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean sector and industry data"""
        if 'sector' in df.columns:
            df['sector'] = df['sector'].str.strip().str.title()
        
        if 'industry' in df.columns:
            df['industry'] = df['industry'].str.strip().str.title()
        
        return df
    
    def deduplicate_data(self, df: pd.DataFrame, subset: List[str], keep: str = 'last') -> pd.DataFrame:
        """Remove duplicates based on specified columns"""
        original_count = len(df)
        df_deduplicated = df.drop_duplicates(subset=subset, keep=keep)
        deduplicated_count = len(df_deduplicated)
        
        self.logger.info(f"Deduplicated data: {original_count} -> {deduplicated_count} rows")
        
        return df_deduplicated
    
    def normalize_timezone(self, df: pd.DataFrame, date_column: str = 'date', timezone: str = 'UTC') -> pd.DataFrame:
        """Normalize timezone for date columns"""
        if date_column in df.columns:
            df[date_column] = pd.to_datetime(df[date_column])
            if df[date_column].dt.tz is None:
                df[date_column] = df[date_column].dt.tz_localize('UTC')
            df[date_column] = df[date_column].dt.tz_convert(timezone)
        
        return df
    
    def validate_data_quality(self, df: pd.DataFrame, data_type: str) -> Dict[str, Any]:
        """Validate data quality and return quality metrics"""
        quality_metrics = {
            'total_rows': len(df),
            'null_counts': df.isnull().sum().to_dict(),
            'duplicate_rows': df.duplicated().sum(),
            'data_types': df.dtypes.to_dict()
        }
        
        if data_type == 'price_data':
            # Price-specific validations
            if 'close_price' in df.columns:
                quality_metrics['negative_prices'] = (df['close_price'] <= 0).sum()
                quality_metrics['zero_prices'] = (df['close_price'] == 0).sum()
            
            if 'volume' in df.columns:
                quality_metrics['negative_volume'] = (df['volume'] < 0).sum()
        
        elif data_type == 'security_data':
            # Security-specific validations
            if 'symbol' in df.columns:
                quality_metrics['empty_symbols'] = df['symbol'].isnull().sum()
                quality_metrics['duplicate_symbols'] = df['symbol'].duplicated().sum()
        
        return quality_metrics
