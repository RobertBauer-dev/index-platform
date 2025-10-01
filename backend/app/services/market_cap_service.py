"""
Market Cap Data Service
Fetches market capitalization data from external APIs
"""
import requests
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import time

from app.core.config import settings


class MarketCapService:
    """Service for fetching market cap data from external sources"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def fetch_from_alpha_vantage(self, symbol: str) -> Optional[float]:
        """Fetch market cap from Alpha Vantage API"""
        if not settings.ALPHA_VANTAGE_API_KEY:
            self.logger.warning("Alpha Vantage API key not configured")
            return None
        
        try:
            # Use the OVERVIEW endpoint which includes market cap
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'OVERVIEW',
                'symbol': symbol,
                'apikey': settings.ALPHA_VANTAGE_API_KEY
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Check for API errors
            if 'Error Message' in data:
                self.logger.error(f"Alpha Vantage API Error for {symbol}: {data['Error Message']}")
                return None
            
            if 'Note' in data:
                self.logger.warning(f"Alpha Vantage API Limit for {symbol}: {data['Note']}")
                return None
            
            # Extract market cap
            market_cap_str = data.get('MarketCapitalization')
            if market_cap_str and market_cap_str != 'None':
                try:
                    return float(market_cap_str)
                except (ValueError, TypeError):
                    self.logger.warning(f"Invalid market cap value for {symbol}: {market_cap_str}")
                    return None
            
            return None
            
        except requests.RequestException as e:
            self.logger.error(f"Alpha Vantage API request failed for {symbol}: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Error fetching market cap from Alpha Vantage for {symbol}: {str(e)}")
            return None
    
    def fetch_from_yahoo_finance(self, symbol: str) -> Optional[float]:
        """Fetch market cap from Yahoo Finance API"""
        try:
            # Yahoo Finance doesn't have a direct API, but we can try to scrape or use alternative
            # For now, we'll use a free alternative API like Financial Modeling Prep
            return self._fetch_from_fmp(symbol)
            
        except Exception as e:
            self.logger.error(f"Error fetching market cap from Yahoo Finance for {symbol}: {str(e)}")
            return None
    
    def _fetch_from_fmp(self, symbol: str) -> Optional[float]:
        """Fetch market cap from Financial Modeling Prep (free tier available)"""
        try:
            # This is a placeholder - you would need to register for FMP API key
            # For demonstration, we'll return None
            self.logger.info(f"Financial Modeling Prep integration not implemented for {symbol}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error fetching from FMP for {symbol}: {str(e)}")
            return None
    
    def fetch_from_polygon(self, symbol: str) -> Optional[float]:
        """Fetch market cap from Polygon.io API"""
        if not hasattr(settings, 'POLYGON_API_KEY') or not settings.POLYGON_API_KEY:
            self.logger.warning("Polygon API key not configured")
            return None
        
        try:
            url = f"https://api.polygon.io/v3/reference/tickers/{symbol}"
            params = {
                'apikey': settings.POLYGON_API_KEY
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'OK' and 'results' in data:
                results = data['results']
                market_cap = results.get('market_cap')
                if market_cap:
                    return float(market_cap)
            
            return None
            
        except requests.RequestException as e:
            self.logger.error(f"Polygon API request failed for {symbol}: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Error fetching market cap from Polygon for {symbol}: {str(e)}")
            return None
    
    def fetch_market_cap(self, symbol: str, source: str = "auto") -> Optional[float]:
        """Fetch market cap from specified source or try multiple sources"""
        if source == "auto":
            # Try multiple sources in order of preference
            sources = ["alpha_vantage", "polygon", "yahoo_finance"]
        else:
            sources = [source]
        
        for source_name in sources:
            try:
                if source_name == "alpha_vantage":
                    market_cap = self.fetch_from_alpha_vantage(symbol)
                elif source_name == "polygon":
                    market_cap = self.fetch_from_polygon(symbol)
                elif source_name == "yahoo_finance":
                    market_cap = self.fetch_from_yahoo_finance(symbol)
                else:
                    continue
                
                if market_cap is not None:
                    self.logger.info(f"Successfully fetched market cap for {symbol}: ${market_cap:,.0f} from {source_name}")
                    return market_cap
                
                # Rate limiting between API calls
                if source == "auto" and len(sources) > 1:
                    time.sleep(1)
                    
            except Exception as e:
                self.logger.warning(f"Failed to fetch market cap for {symbol} from {source_name}: {str(e)}")
                continue
        
        self.logger.warning(f"Failed to fetch market cap for {symbol} from all sources")
        return None
    
    def batch_fetch_market_caps(self, symbols: List[str], source: str = "auto") -> Dict[str, Optional[float]]:
        """Fetch market cap for multiple symbols"""
        results = {}
        
        for i, symbol in enumerate(symbols):
            try:
                market_cap = self.fetch_market_cap(symbol, source)
                results[symbol] = market_cap
                
                # Rate limiting for batch requests
                if i < len(symbols) - 1:  # Don't sleep after the last request
                    time.sleep(2)  # Wait 2 seconds between requests
                    
            except Exception as e:
                self.logger.error(f"Error in batch fetch for {symbol}: {str(e)}")
                results[symbol] = None
        
        return results
    
    def calculate_market_cap_from_price_and_shares(self, price: float, shares: float) -> Optional[float]:
        """Calculate market cap from current price and outstanding shares"""
        try:
            if price and shares and price > 0 and shares > 0:
                return price * shares
            return None
        except (ValueError, TypeError) as e:
            self.logger.error(f"Error calculating market cap from price {price} and shares {shares}: {str(e)}")
            return None
