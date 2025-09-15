"""
Index calculation engine with various weighting methods
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import logging

from app.db import models
from app.processing.data_transformer import DataTransformer


class WeightingMethod(ABC):
    """Abstract base class for weighting methods"""
    
    @abstractmethod
    def calculate_weights(self, constituents: pd.DataFrame) -> pd.DataFrame:
        """Calculate weights for index constituents"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get the name of the weighting method"""
        pass


class EqualWeight(WeightingMethod):
    """Equal weight weighting method"""
    
    def calculate_weights(self, constituents: pd.DataFrame) -> pd.DataFrame:
        """Calculate equal weights"""
        df = constituents.copy()
        df['weight'] = 1.0 / len(df)
        return df
    
    def get_name(self) -> str:
        return "equal_weight"


class MarketCapWeight(WeightingMethod):
    """Market capitalization weighted method"""
    
    def calculate_weights(self, constituents: pd.DataFrame) -> pd.DataFrame:
        """Calculate market cap weights"""
        df = constituents.copy()
        
        if 'market_cap' not in df.columns:
            # Calculate market cap if not present
            if 'close_price' in df.columns and 'shares' in df.columns:
                df['market_cap'] = df['close_price'] * df['shares']
            else:
                # Fallback to equal weight if no market cap data
                df['weight'] = 1.0 / len(df)
                return df
        
        total_market_cap = df['market_cap'].sum()
        df['weight'] = df['market_cap'] / total_market_cap
        
        return df
    
    def get_name(self) -> str:
        return "market_cap_weight"


class PriceWeight(WeightingMethod):
    """Price weighted method (like Dow Jones)"""
    
    def calculate_weights(self, constituents: pd.DataFrame) -> pd.DataFrame:
        """Calculate price weights"""
        df = constituents.copy()
        
        if 'close_price' not in df.columns:
            raise ValueError("Price data required for price weighting")
        
        total_price = df['close_price'].sum()
        df['weight'] = df['close_price'] / total_price
        
        return df
    
    def get_name(self) -> str:
        return "price_weight"


class RevenueWeight(WeightingMethod):
    """Revenue weighted method"""
    
    def calculate_weights(self, constituents: pd.DataFrame) -> pd.DataFrame:
        """Calculate revenue weights"""
        df = constituents.copy()
        
        if 'revenue' not in df.columns:
            raise ValueError("Revenue data required for revenue weighting")
        
        total_revenue = df['revenue'].sum()
        df['weight'] = df['revenue'] / total_revenue
        
        return df
    
    def get_name(self) -> str:
        return "revenue_weight"


class ESGWeight(WeightingMethod):
    """ESG score weighted method"""
    
    def calculate_weights(self, constituents: pd.DataFrame) -> pd.DataFrame:
        """Calculate ESG weights"""
        df = constituents.copy()
        
        if 'esg_score' not in df.columns:
            # Fallback to equal weight if no ESG data
            df['weight'] = 1.0 / len(df)
            return df
        
        # Normalize ESG scores (0-100 scale)
        df['esg_normalized'] = df['esg_score'] / 100.0
        
        # Use ESG score as weight multiplier
        total_esg_weight = df['esg_normalized'].sum()
        df['weight'] = df['esg_normalized'] / total_esg_weight
        
        return df
    
    def get_name(self) -> str:
        return "esg_weight"


class IndexEngine:
    """Main index calculation engine"""
    
    def __init__(self, db_session):
        self.db = db_session
        self.data_transformer = DataTransformer()
        self.logger = logging.getLogger(__name__)
        
        # Register weighting methods
        self.weighting_methods = {
            'equal_weight': EqualWeight(),
            'market_cap_weight': MarketCapWeight(),
            'price_weight': PriceWeight(),
            'revenue_weight': RevenueWeight(),
            'esg_weight': ESGWeight()
        }
    
    def calculate_index(self, index_definition_id: int, date: datetime = None) -> Dict[str, Any]:
        """Calculate index value for a specific date"""
        if not date:
            date = datetime.now()
        
        try:
            # Get index definition
            index_def = self.db.query(models.IndexDefinition).filter(
                models.IndexDefinition.id == index_definition_id
            ).first()
            
            if not index_def:
                return {"error": "Index definition not found"}
            
            # Get constituents for the date
            constituents = self._get_constituents(index_definition_id, date)
            
            if constituents.empty:
                return {"error": "No constituents found for the date"}
            
            # Apply filters
            filtered_constituents = self._apply_filters(constituents, index_def)
            
            # Calculate weights
            weighting_method = self.weighting_methods.get(index_def.weighting_method)
            if not weighting_method:
                return {"error": f"Unknown weighting method: {index_def.weighting_method}"}
            
            weighted_constituents = weighting_method.calculate_weights(filtered_constituents)
            
            # Calculate index value
            index_value = self._calculate_index_value(weighted_constituents, index_def.weighting_method)
            
            # Calculate performance metrics
            performance_metrics = self._calculate_performance_metrics(index_definition_id, date)
            
            return {
                "index_value": index_value,
                "constituents_count": len(weighted_constituents),
                "weighting_method": index_def.weighting_method,
                "date": date,
                "constituents": weighted_constituents.to_dict('records'),
                "performance_metrics": performance_metrics
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating index: {str(e)}")
            return {"error": str(e)}
    
    def calculate_index_series(self, index_definition_id: int, start_date: datetime, 
                              end_date: datetime) -> pd.DataFrame:
        """Calculate index values for a date range"""
        try:
            # Get index definition
            index_def = self.db.query(models.IndexDefinition).filter(
                models.IndexDefinition.id == index_definition_id
            ).first()
            
            if not index_def:
                raise ValueError("Index definition not found")
            
            # Generate date range (business days only)
            date_range = pd.bdate_range(start=start_date, end=end_date)
            
            index_values = []
            
            for date in date_range:
                result = self.calculate_index(index_definition_id, date)
                
                if 'error' not in result:
                    index_values.append({
                        'date': date,
                        'index_value': result['index_value'],
                        'constituents_count': result['constituents_count']
                    })
            
            return pd.DataFrame(index_values)
            
        except Exception as e:
            self.logger.error(f"Error calculating index series: {str(e)}")
            return pd.DataFrame()
    
    def rebalance_index(self, index_definition_id: int, date: datetime = None) -> Dict[str, Any]:
        """Rebalance index constituents"""
        if not date:
            date = datetime.now()
        
        try:
            # Get index definition
            index_def = self.db.query(models.IndexDefinition).filter(
                models.IndexDefinition.id == index_definition_id
            ).first()
            
            if not index_def:
                return {"error": "Index definition not found"}
            
            # Get current constituents
            current_constituents = self._get_current_constituents(index_definition_id)
            
            # Calculate new constituents based on criteria
            new_constituents = self._calculate_new_constituents(index_definition_id, date)
            
            # Determine additions and removals
            current_symbols = set(current_constituents['symbol'].tolist())
            new_symbols = set(new_constituents['symbol'].tolist())
            
            additions = new_symbols - current_symbols
            removals = current_symbols - new_symbols
            
            # Calculate new weights
            weighting_method = self.weighting_methods.get(index_def.weighting_method)
            weighted_constituents = weighting_method.calculate_weights(new_constituents)
            
            # Save new constituents
            self._save_constituents(index_definition_id, weighted_constituents, date, additions, removals)
            
            return {
                "additions": list(additions),
                "removals": list(removals),
                "new_constituents_count": len(new_constituents),
                "date": date
            }
            
        except Exception as e:
            self.logger.error(f"Error rebalancing index: {str(e)}")
            return {"error": str(e)}
    
    def backtest_index(self, index_definition_id: int, start_date: datetime, 
                      end_date: datetime, rebalance_frequency: str = 'monthly') -> Dict[str, Any]:
        """Backtest index performance"""
        try:
            # Calculate index series
            index_series = self.calculate_index_series(index_definition_id, start_date, end_date)
            
            if index_series.empty:
                return {"error": "No index data calculated"}
            
            # Calculate performance metrics
            performance_metrics = self._calculate_backtest_metrics(index_series)
            
            # Calculate returns
            index_series['daily_return'] = index_series['index_value'].pct_change()
            index_series['cumulative_return'] = (1 + index_series['daily_return']).cumprod() - 1
            
            return {
                "index_series": index_series.to_dict('records'),
                "performance_metrics": performance_metrics,
                "start_date": start_date,
                "end_date": end_date,
                "total_return": index_series['cumulative_return'].iloc[-1] if not index_series.empty else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error backtesting index: {str(e)}")
            return {"error": str(e)}
    
    def _get_constituents(self, index_definition_id: int, date: datetime) -> pd.DataFrame:
        """Get index constituents for a specific date"""
        # Get the most recent constituents before or on the given date
        constituents = self.db.query(models.IndexConstituent).filter(
            models.IndexConstituent.index_definition_id == index_definition_id,
            models.IndexConstituent.date <= date,
            models.IndexConstituent.is_removal == False
        ).order_by(models.IndexConstituent.date.desc()).all()
        
        if not constituents:
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame([{
            'security_id': c.security_id,
            'weight': c.weight,
            'shares': c.shares,
            'market_cap': c.market_cap,
            'date': c.date
        } for c in constituents])
        
        # Get latest constituents for each security
        latest_constituents = df.sort_values('date').groupby('security_id').tail(1)
        
        # Get security information
        security_ids = latest_constituents['security_id'].tolist()
        securities = self.db.query(models.Security).filter(
            models.Security.id.in_(security_ids)
        ).all()
        
        security_map = {s.id: {'symbol': s.symbol, 'name': s.name, 'sector': s.sector, 
                             'country': s.country, 'market_cap': s.market_cap} for s in securities}
        
        # Add security information
        for col, values in security_map.items():
            for security_id, info in values.items():
                latest_constituents.loc[latest_constituents['security_id'] == security_id, col] = info
        
        # Get latest price data
        price_data = self.db.query(models.PriceData).filter(
            models.PriceData.security_id.in_(security_ids),
            models.PriceData.date <= date
        ).order_by(models.PriceData.date.desc()).all()
        
        # Get latest price for each security
        latest_prices = {}
        for price in price_data:
            if price.security_id not in latest_prices:
                latest_prices[price.security_id] = {
                    'close_price': price.close_price,
                    'open_price': price.open_price,
                    'high_price': price.high_price,
                    'low_price': price.low_price,
                    'volume': price.volume
                }
        
        # Add price information
        for security_id, price_info in latest_prices.items():
            for col, value in price_info.items():
                latest_constituents.loc[latest_constituents['security_id'] == security_id, col] = value
        
        return latest_constituents
    
    def _apply_filters(self, constituents: pd.DataFrame, index_def: models.IndexDefinition) -> pd.DataFrame:
        """Apply index filters to constituents"""
        filtered_df = constituents.copy()
        
        # Market cap filters
        if index_def.min_market_cap:
            filtered_df = filtered_df[filtered_df['market_cap'] >= index_def.min_market_cap]
        
        if index_def.max_market_cap:
            filtered_df = filtered_df[filtered_df['market_cap'] <= index_def.max_market_cap]
        
        # Sector filter
        if index_def.sectors:
            try:
                import json
                allowed_sectors = json.loads(index_def.sectors)
                filtered_df = filtered_df[filtered_df['sector'].isin(allowed_sectors)]
            except:
                pass
        
        # Country filter
        if index_def.countries:
            try:
                import json
                allowed_countries = json.loads(index_def.countries)
                filtered_df = filtered_df[filtered_df['country'].isin(allowed_countries)]
            except:
                pass
        
        # Max constituents
        if index_def.max_constituents:
            filtered_df = filtered_df.nlargest(index_def.max_constituents, 'market_cap')
        
        return filtered_df
    
    def _calculate_index_value(self, constituents: pd.DataFrame, weighting_method: str) -> float:
        """Calculate index value based on constituents and weighting method"""
        if constituents.empty:
            return 0.0
        
        if weighting_method == 'equal_weight':
            return constituents['close_price'].mean()
        
        elif weighting_method == 'market_cap_weight':
            if 'market_cap' in constituents.columns:
                total_market_cap = constituents['market_cap'].sum()
                return (constituents['close_price'] * constituents['market_cap']).sum() / total_market_cap
            else:
                return constituents['close_price'].mean()
        
        elif weighting_method == 'price_weight':
            total_price = constituents['close_price'].sum()
            return (constituents['close_price'] ** 2).sum() / total_price
        
        else:
            return constituents['close_price'].mean()
    
    def _calculate_performance_metrics(self, index_definition_id: int, date: datetime) -> Dict[str, float]:
        """Calculate performance metrics for the index"""
        try:
            # Get historical index values
            historical_values = self.db.query(models.IndexValue).filter(
                models.IndexValue.index_definition_id == index_definition_id,
                models.IndexValue.date <= date
            ).order_by(models.IndexValue.date.desc()).limit(252).all()  # Last year
            
            if len(historical_values) < 2:
                return {}
            
            # Convert to DataFrame
            df = pd.DataFrame([{
                'date': v.date,
                'index_value': v.index_value
            } for v in historical_values])
            
            df = df.sort_values('date')
            df['daily_return'] = df['index_value'].pct_change()
            
            # Calculate metrics
            metrics = {
                'total_return_1d': df['daily_return'].iloc[-1] if len(df) > 0 else 0,
                'total_return_1w': df['daily_return'].tail(5).sum() if len(df) >= 5 else 0,
                'total_return_1m': df['daily_return'].tail(20).sum() if len(df) >= 20 else 0,
                'total_return_3m': df['daily_return'].tail(60).sum() if len(df) >= 60 else 0,
                'total_return_1y': df['daily_return'].sum() if len(df) >= 252 else 0,
                'volatility': df['daily_return'].std() * np.sqrt(252) if len(df) > 1 else 0,
                'sharpe_ratio': self._calculate_sharpe_ratio(df['daily_return']) if len(df) > 1 else 0,
                'max_drawdown': self._calculate_max_drawdown(df['index_value']) if len(df) > 1 else 0
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating performance metrics: {str(e)}")
            return {}
    
    def _calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        if len(returns) < 2:
            return 0.0
        
        excess_returns = returns - (risk_free_rate / 252)
        return (excess_returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0.0
    
    def _calculate_max_drawdown(self, values: pd.Series) -> float:
        """Calculate maximum drawdown"""
        if len(values) < 2:
            return 0.0
        
        cumulative = (1 + values.pct_change()).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        
        return drawdown.min()
    
    def _get_current_constituents(self, index_definition_id: int) -> pd.DataFrame:
        """Get current index constituents"""
        constituents = self.db.query(models.IndexConstituent).filter(
            models.IndexConstituent.index_definition_id == index_definition_id,
            models.IndexConstituent.is_removal == False
        ).all()
        
        if not constituents:
            return pd.DataFrame()
        
        # Get security information
        security_ids = [c.security_id for c in constituents]
        securities = self.db.query(models.Security).filter(
            models.Security.id.in_(security_ids)
        ).all()
        
        security_map = {s.id: s.symbol for s in securities}
        
        df = pd.DataFrame([{
            'security_id': c.security_id,
            'symbol': security_map.get(c.security_id, ''),
            'weight': c.weight
        } for c in constituents])
        
        return df
    
    def _calculate_new_constituents(self, index_definition_id: int, date: datetime) -> pd.DataFrame:
        """Calculate new constituents based on index criteria"""
        # This would implement the logic to select new constituents
        # based on the index definition criteria (market cap, sector, etc.)
        # For now, return empty DataFrame
        return pd.DataFrame()
    
    def _save_constituents(self, index_definition_id: int, constituents: pd.DataFrame, 
                          date: datetime, additions: set, removals: set):
        """Save new constituents to database"""
        # Mark removals
        for symbol in removals:
            security = self.db.query(models.Security).filter(
                models.Security.symbol == symbol
            ).first()
            
            if security:
                constituent = self.db.query(models.IndexConstituent).filter(
                    models.IndexConstituent.index_definition_id == index_definition_id,
                    models.IndexConstituent.security_id == security.id,
                    models.IndexConstituent.is_removal == False
                ).first()
                
                if constituent:
                    constituent.is_removal = True
                    constituent.date = date
        
        # Add new constituents
        for _, row in constituents.iterrows():
            new_constituent = models.IndexConstituent(
                index_definition_id=index_definition_id,
                security_id=row['security_id'],
                date=date,
                weight=row['weight'],
                shares=row.get('shares'),
                market_cap=row.get('market_cap'),
                is_new_addition=row['symbol'] in additions
            )
            self.db.add(new_constituent)
        
        self.db.commit()
    
    def _calculate_backtest_metrics(self, index_series: pd.DataFrame) -> Dict[str, float]:
        """Calculate backtest performance metrics"""
        if index_series.empty:
            return {}
        
        returns = index_series['index_value'].pct_change().dropna()
        
        if len(returns) < 2:
            return {}
        
        metrics = {
            'total_return': (index_series['index_value'].iloc[-1] / index_series['index_value'].iloc[0]) - 1,
            'annualized_return': (1 + returns.mean()) ** 252 - 1,
            'volatility': returns.std() * np.sqrt(252),
            'sharpe_ratio': self._calculate_sharpe_ratio(returns),
            'max_drawdown': self._calculate_max_drawdown(index_series['index_value']),
            'win_rate': (returns > 0).mean(),
            'avg_win': returns[returns > 0].mean() if len(returns[returns > 0]) > 0 else 0,
            'avg_loss': returns[returns < 0].mean() if len(returns[returns < 0]) > 0 else 0
        }
        
        return metrics
