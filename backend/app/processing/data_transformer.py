"""
Data transformation utilities
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import logging


class DataTransformer:
    """Data transformation utilities"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_returns(self, df: pd.DataFrame, price_column: str = 'close_price', 
                         periods: List[int] = [1, 5, 10, 20, 252]) -> pd.DataFrame:
        """Calculate various return periods"""
        df_sorted = df.sort_values(['security_id', 'date'])
        
        for period in periods:
            if period == 1:
                # Daily returns
                df_sorted[f'daily_return'] = df_sorted.groupby('security_id')[price_column].pct_change()
            else:
                # Multi-period returns
                df_sorted[f'return_{period}d'] = df_sorted.groupby('security_id')[price_column].pct_change(periods=period)
        
        return df_sorted
    
    def calculate_volatility(self, df: pd.DataFrame, return_column: str = 'daily_return', 
                           window: int = 20, annualize: bool = True) -> pd.DataFrame:
        """Calculate rolling volatility"""
        df_sorted = df.sort_values(['security_id', 'date'])
        
        # Calculate rolling standard deviation
        volatility = df_sorted.groupby('security_id')[return_column].rolling(window=window).std()
        
        if annualize:
            # Annualize volatility (assuming 252 trading days)
            volatility = volatility * np.sqrt(252)
        
        df_sorted[f'volatility_{window}d'] = volatility.values
        
        return df_sorted
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators"""
        df_sorted = df.sort_values(['security_id', 'date'])
        
        for security_id in df_sorted['security_id'].unique():
            security_data = df_sorted[df_sorted['security_id'] == security_id].copy()
            
            # Moving averages
            security_data['sma_20'] = security_data['close_price'].rolling(window=20).mean()
            security_data['sma_50'] = security_data['close_price'].rolling(window=50).mean()
            security_data['sma_200'] = security_data['close_price'].rolling(window=200).mean()
            
            # Exponential moving averages
            security_data['ema_12'] = security_data['close_price'].ewm(span=12).mean()
            security_data['ema_26'] = security_data['close_price'].ewm(span=26).mean()
            
            # MACD
            security_data['macd'] = security_data['ema_12'] - security_data['ema_26']
            security_data['macd_signal'] = security_data['macd'].ewm(span=9).mean()
            security_data['macd_histogram'] = security_data['macd'] - security_data['macd_signal']
            
            # RSI
            security_data['rsi'] = self._calculate_rsi(security_data['close_price'])
            
            # Bollinger Bands
            security_data['bb_middle'] = security_data['close_price'].rolling(window=20).mean()
            bb_std = security_data['close_price'].rolling(window=20).std()
            security_data['bb_upper'] = security_data['bb_middle'] + (bb_std * 2)
            security_data['bb_lower'] = security_data['bb_middle'] - (bb_std * 2)
            
            # Update the main dataframe
            df_sorted.loc[df_sorted['security_id'] == security_id, 
                         ['sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_26', 
                          'macd', 'macd_signal', 'macd_histogram', 'rsi',
                          'bb_middle', 'bb_upper', 'bb_lower']] = security_data[
                         ['sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_26',
                          'macd', 'macd_signal', 'macd_histogram', 'rsi',
                          'bb_middle', 'bb_upper', 'bb_lower']].values
        
        return df_sorted
    
    def calculate_market_cap(self, df: pd.DataFrame, shares_column: str = 'shares') -> pd.DataFrame:
        """Calculate market capitalization"""
        if 'close_price' in df.columns and shares_column in df.columns:
            df['market_cap'] = df['close_price'] * df[shares_column]
        
        return df
    
    def calculate_performance_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate performance metrics"""
        df_sorted = df.sort_values(['security_id', 'date'])
        
        for security_id in df_sorted['security_id'].unique():
            security_data = df_sorted[df_sorted['security_id'] == security_id].copy()
            
            # Calculate returns
            security_data['daily_return'] = security_data['close_price'].pct_change()
            
            # Calculate cumulative returns
            security_data['cumulative_return'] = (1 + security_data['daily_return']).cumprod() - 1
            
            # Calculate rolling metrics
            security_data['rolling_return_1m'] = security_data['daily_return'].rolling(window=20).mean()
            security_data['rolling_return_3m'] = security_data['daily_return'].rolling(window=60).mean()
            security_data['rolling_return_1y'] = security_data['daily_return'].rolling(window=252).mean()
            
            # Calculate Sharpe ratio (annualized)
            risk_free_rate = 0.02  # 2% annual risk-free rate
            excess_return = security_data['daily_return'] - (risk_free_rate / 252)
            security_data['sharpe_ratio'] = (excess_return.rolling(window=252).mean() / 
                                           excess_return.rolling(window=252).std()) * np.sqrt(252)
            
            # Calculate maximum drawdown
            security_data['cumulative_max'] = security_data['cumulative_return'].cummax()
            security_data['drawdown'] = security_data['cumulative_return'] - security_data['cumulative_max']
            security_data['max_drawdown'] = security_data['drawdown'].cummin()
            
            # Update the main dataframe
            df_sorted.loc[df_sorted['security_id'] == security_id, 
                         ['daily_return', 'cumulative_return', 'rolling_return_1m', 
                          'rolling_return_3m', 'rolling_return_1y', 'sharpe_ratio',
                          'drawdown', 'max_drawdown']] = security_data[
                         ['daily_return', 'cumulative_return', 'rolling_return_1m',
                          'rolling_return_3m', 'rolling_return_1y', 'sharpe_ratio',
                          'drawdown', 'max_drawdown']].values
        
        return df_sorted
    
    def resample_data(self, df: pd.DataFrame, frequency: str = 'M') -> pd.DataFrame:
        """Resample data to different frequencies"""
        df_sorted = df.sort_values(['security_id', 'date'])
        
        resampled_data = []
        
        for security_id in df_sorted['security_id'].unique():
            security_data = df_sorted[df_sorted['security_id'] == security_id].copy()
            security_data = security_data.set_index('date')
            
            # Resample to specified frequency
            resampled = security_data.resample(frequency).agg({
                'open_price': 'first',
                'high_price': 'max',
                'low_price': 'min',
                'close_price': 'last',
                'volume': 'sum',
                'adjusted_close': 'last'
            }).dropna()
            
            resampled['security_id'] = security_id
            resampled = resampled.reset_index()
            
            resampled_data.append(resampled)
        
        if resampled_data:
            return pd.concat(resampled_data, ignore_index=True)
        else:
            return pd.DataFrame()
    
    def calculate_index_constituents(self, df: pd.DataFrame, date: datetime, 
                                   filters: Dict[str, Any]) -> pd.DataFrame:
        """Calculate index constituents based on filters"""
        # Apply filters
        filtered_df = df.copy()
        
        # Date filter
        if 'date' in filters:
            filtered_df = filtered_df[filtered_df['date'] <= date]
        
        # Get latest data for each security
        latest_data = filtered_df.sort_values('date').groupby('security_id').tail(1)
        
        # Market cap filter
        if 'min_market_cap' in filters:
            latest_data = latest_data[latest_data['market_cap'] >= filters['min_market_cap']]
        
        if 'max_market_cap' in filters:
            latest_data = latest_data[latest_data['market_cap'] <= filters['max_market_cap']]
        
        # Sector filter
        if 'sectors' in filters and filters['sectors']:
            latest_data = latest_data[latest_data['sector'].isin(filters['sectors'])]
        
        # Country filter
        if 'countries' in filters and filters['countries']:
            latest_data = latest_data[latest_data['country'].isin(filters['countries'])]
        
        # Sort by market cap and limit
        if 'max_constituents' in filters:
            latest_data = latest_data.nlargest(filters['max_constituents'], 'market_cap')
        
        return latest_data
    
    def _calculate_rsi(self, prices: pd.Series, window: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def create_portfolio_weights(self, df: pd.DataFrame, method: str = 'equal_weight') -> pd.DataFrame:
        """Create portfolio weights based on specified method"""
        if method == 'equal_weight':
            df['weight'] = 1.0 / len(df)
        
        elif method == 'market_cap_weight':
            total_market_cap = df['market_cap'].sum()
            df['weight'] = df['market_cap'] / total_market_cap
        
        elif method == 'price_weight':
            total_price = df['close_price'].sum()
            df['weight'] = df['close_price'] / total_price
        
        else:
            raise ValueError(f"Unknown weighting method: {method}")
        
        return df
