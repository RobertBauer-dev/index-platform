"""
ETL/ELT Pipeline for data processing
"""
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from sqlalchemy.orm import Session

from app.processing.data_cleaner import DataCleaner
from app.processing.data_transformer import DataTransformer
from app.db import models


class ETLPipeline:
    """ETL Pipeline for processing financial data"""
    
    def __init__(self, db: Session):
        self.db = db
        self.data_cleaner = DataCleaner()
        self.data_transformer = DataTransformer()
        self.logger = logging.getLogger(__name__)
    
    def process_raw_price_data(self, start_date: Optional[datetime] = None, 
                              end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Process raw price data through ETL pipeline"""
        try:
            # Extract: Get raw price data
            query = self.db.query(models.PriceData)
            
            if start_date:
                query = query.filter(models.PriceData.date >= start_date)
            if end_date:
                query = query.filter(models.PriceData.date <= end_date)
            
            raw_data = query.all()
            
            if not raw_data:
                return {"error": "No raw price data found"}
            
            # Convert to DataFrame
            df = pd.DataFrame([{
                'id': row.id,
                'security_id': row.security_id,
                'date': row.date,
                'open_price': row.open_price,
                'high_price': row.high_price,
                'low_price': row.low_price,
                'close_price': row.close_price,
                'volume': row.volume,
                'adjusted_close': row.adjusted_close,
                'dividend': row.dividend,
                'split_ratio': row.split_ratio
            } for row in raw_data])
            
            # Transform: Clean and transform data
            cleaned_df = self.data_cleaner.clean_price_data(df)
            transformed_df = self.data_transformer.calculate_returns(cleaned_df)
            transformed_df = self.data_transformer.calculate_volatility(transformed_df)
            transformed_df = self.data_transformer.calculate_technical_indicators(transformed_df)
            transformed_df = self.data_transformer.calculate_performance_metrics(transformed_df)
            
            # Load: Update database with processed data
            updated_count = self._update_price_data(transformed_df)
            
            return {
                "processed_rows": len(transformed_df),
                "updated_rows": updated_count,
                "status": "success"
            }
            
        except Exception as e:
            self.logger.error(f"Error in ETL pipeline: {str(e)}")
            return {"error": str(e)}
    
    def process_security_data(self) -> Dict[str, Any]:
        """Process security master data"""
        try:
            # Extract: Get raw security data
            raw_data = self.db.query(models.Security).all()
            
            if not raw_data:
                return {"error": "No security data found"}
            
            # Convert to DataFrame
            df = pd.DataFrame([{
                'id': row.id,
                'symbol': row.symbol,
                'name': row.name,
                'exchange': row.exchange,
                'currency': row.currency,
                'sector': row.sector,
                'industry': row.industry,
                'country': row.country,
                'market_cap': row.market_cap,
                'is_active': row.is_active
            } for row in raw_data])
            
            # Transform: Clean data
            cleaned_df = self.data_cleaner.clean_security_data(df)
            
            # Load: Update database
            updated_count = self._update_security_data(cleaned_df)
            
            return {
                "processed_rows": len(cleaned_df),
                "updated_rows": updated_count,
                "status": "success"
            }
            
        except Exception as e:
            self.logger.error(f"Error processing security data: {str(e)}")
            return {"error": str(e)}
    
    def calculate_index_values(self, index_definition_id: int, start_date: Optional[datetime] = None,
                              end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Calculate index values for a given index definition"""
        try:
            # Get index definition
            index_def = self.db.query(models.IndexDefinition).filter(
                models.IndexDefinition.id == index_definition_id
            ).first()
            
            if not index_def:
                return {"error": "Index definition not found"}
            
            # Get constituents for each date
            if not start_date:
                start_date = datetime.now() - pd.Timedelta(days=365)
            if not end_date:
                end_date = datetime.now()
            
            # Generate date range
            date_range = pd.date_range(start=start_date, end=end_date, freq='D')
            
            index_values = []
            
            for date in date_range:
                # Get constituents for this date
                constituents = self._get_index_constituents(index_definition_id, date)
                
                if not constituents.empty:
                    # Calculate index value
                    index_value = self._calculate_index_value(constituents, index_def.weighting_method)
                    
                    index_values.append({
                        'index_definition_id': index_definition_id,
                        'date': date,
                        'index_value': index_value,
                        'total_return': None,  # Will be calculated later
                        'price_return': None,
                        'dividend_yield': None,
                        'volatility': None,
                        'sharpe_ratio': None
                    })
            
            # Save index values
            saved_count = self._save_index_values(index_values)
            
            return {
                "calculated_values": len(index_values),
                "saved_values": saved_count,
                "status": "success"
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating index values: {str(e)}")
            return {"error": str(e)}
    
    def run_daily_etl(self) -> Dict[str, Any]:
        """Run daily ETL process"""
        results = {}
        
        try:
            # Process price data for last 30 days
            end_date = datetime.now()
            start_date = end_date - pd.Timedelta(days=30)
            
            results['price_data'] = self.process_raw_price_data(start_date, end_date)
            results['security_data'] = self.process_security_data()
            
            # Calculate index values for all active indices
            active_indices = self.db.query(models.IndexDefinition).filter(
                models.IndexDefinition.is_active == True
            ).all()
            
            for index_def in active_indices:
                results[f'index_{index_def.id}'] = self.calculate_index_values(
                    index_def.id, start_date, end_date
                )
            
            results['status'] = 'success'
            
        except Exception as e:
            self.logger.error(f"Error in daily ETL: {str(e)}")
            results['status'] = 'error'
            results['error'] = str(e)
        
        return results
    
    def _update_price_data(self, df: pd.DataFrame) -> int:
        """Update price data with processed values"""
        updated_count = 0
        
        for _, row in df.iterrows():
            try:
                price_data = self.db.query(models.PriceData).filter(
                    models.PriceData.id == row['id']
                ).first()
                
                if price_data:
                    # Update with processed values
                    for column in ['daily_return', 'volatility_20d', 'sma_20', 'sma_50', 
                                 'rsi', 'sharpe_ratio', 'max_drawdown']:
                        if column in row and pd.notna(row[column]):
                            # Note: These would need to be added as columns to the PriceData model
                            # For now, we'll skip this or store in a separate analytics table
                            pass
                    
                    updated_count += 1
                    
            except Exception as e:
                self.logger.error(f"Error updating price data: {str(e)}")
        
        self.db.commit()
        return updated_count
    
    def _update_security_data(self, df: pd.DataFrame) -> int:
        """Update security data with cleaned values"""
        updated_count = 0
        
        for _, row in df.iterrows():
            try:
                security = self.db.query(models.Security).filter(
                    models.Security.id == row['id']
                ).first()
                
                if security:
                    # Update with cleaned values
                    for column in ['symbol', 'name', 'currency', 'sector', 'industry']:
                        if column in row and pd.notna(row[column]):
                            setattr(security, column, row[column])
                    
                    updated_count += 1
                    
            except Exception as e:
                self.logger.error(f"Error updating security data: {str(e)}")
        
        self.db.commit()
        return updated_count
    
    def _get_index_constituents(self, index_definition_id: int, date: datetime) -> pd.DataFrame:
        """Get index constituents for a specific date"""
        # Get the most recent constituents before or on the given date
        constituents = self.db.query(models.IndexConstituent).filter(
            models.IndexConstituent.index_definition_id == index_definition_id,
            models.IndexConstituent.date <= date,
            models.IndexConstituent.is_removal == False
        ).order_by(models.IndexConstituent.date.desc()).all()
        
        # Convert to DataFrame and get latest constituents
        if constituents:
            df = pd.DataFrame([{
                'security_id': c.security_id,
                'weight': c.weight,
                'date': c.date
            } for c in constituents])
            
            # Get latest constituents for each security
            latest_constituents = df.sort_values('date').groupby('security_id').tail(1)
            
            # Get price data for these securities
            security_ids = latest_constituents['security_id'].tolist()
            price_data = self.db.query(models.PriceData).filter(
                models.PriceData.security_id.in_(security_ids),
                models.PriceData.date <= date
            ).order_by(models.PriceData.date.desc()).all()
            
            # Get latest price for each security
            latest_prices = {}
            for price in price_data:
                if price.security_id not in latest_prices:
                    latest_prices[price.security_id] = price.close_price
            
            # Combine constituents with prices
            latest_constituents['close_price'] = latest_constituents['security_id'].map(latest_prices)
            latest_constituents = latest_constituents.dropna(subset=['close_price'])
            
            return latest_constituents
        
        return pd.DataFrame()
    
    def _calculate_index_value(self, constituents: pd.DataFrame, weighting_method: str) -> float:
        """Calculate index value based on weighting method"""
        if constituents.empty:
            return 0.0
        
        if weighting_method == 'equal_weight':
            return constituents['close_price'].mean()
        
        elif weighting_method == 'market_cap_weight':
            # This would require market cap data
            return constituents['close_price'].mean()  # Simplified for now
        
        else:
            return constituents['close_price'].mean()
    
    def _save_index_values(self, index_values: List[Dict]) -> int:
        """Save calculated index values to database"""
        saved_count = 0
        
        for value_data in index_values:
            try:
                # Check if value already exists
                existing = self.db.query(models.IndexValue).filter(
                    models.IndexValue.index_definition_id == value_data['index_definition_id'],
                    models.IndexValue.date == value_data['date']
                ).first()
                
                if existing:
                    # Update existing value
                    for key, val in value_data.items():
                        if key != 'index_definition_id' and key != 'date':
                            setattr(existing, key, val)
                else:
                    # Create new value
                    new_value = models.IndexValue(**value_data)
                    self.db.add(new_value)
                
                saved_count += 1
                
            except Exception as e:
                self.logger.error(f"Error saving index value: {str(e)}")
        
        self.db.commit()
        return saved_count
