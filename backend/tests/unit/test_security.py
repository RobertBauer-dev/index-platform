"""
Unit tests for security-related functionality
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, date

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token
)
from app.db.models import Security
from app.db.schemas import SecurityCreate, SecurityUpdate
from app.processing.data_cleaner import DataCleaner
from app.processing.data_transformer import DataTransformer


class TestSecurityFunctions:
    """Test security utility functions"""
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrongpassword", hashed)
    
    def test_token_creation_and_verification(self):
        """Test JWT token creation and verification"""
        user_id = 1
        token = create_access_token(data={"sub": str(user_id)})
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Verify token
        payload = verify_token(token)
        assert payload["sub"] == str(user_id)
    
    def test_invalid_token(self):
        """Test invalid token handling"""
        invalid_token = "invalid.token.here"
        
        with pytest.raises(Exception):
            verify_token(invalid_token)


class TestDataCleaner:
    """Test data cleaning functionality"""
    
    def setup_method(self):
        """Set up test data"""
        self.cleaner = DataCleaner()
        self.sample_data = [
            {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "price": 150.0,
                "currency": "USD",
                "date": "2024-01-01"
            },
            {
                "symbol": "AAPL",  # Duplicate
                "name": "Apple Inc.",
                "price": 151.0,
                "currency": "USD",
                "date": "2024-01-01"
            },
            {
                "symbol": "MSFT",
                "name": "Microsoft Corp.",
                "price": 300.0,
                "currency": "EUR",  # Different currency
                "date": "2024-01-01"
            }
        ]
    
    def test_remove_duplicates(self):
        """Test duplicate removal"""
        cleaned_data = self.cleaner.remove_duplicates(self.sample_data, key="symbol")
        
        assert len(cleaned_data) == 2
        assert cleaned_data[0]["symbol"] == "AAPL"
        assert cleaned_data[1]["symbol"] == "MSFT"
    
    def test_harmonize_currencies(self):
        """Test currency harmonization"""
        # Mock exchange rate
        with patch.object(self.cleaner, 'get_exchange_rate', return_value=0.85):
            harmonized_data = self.cleaner.harmonize_currencies(
                self.sample_data, 
                target_currency="USD"
            )
            
            # EUR price should be converted to USD
            msft_data = next(item for item in harmonized_data if item["symbol"] == "MSFT")
            assert msft_data["currency"] == "USD"
            assert msft_data["price"] == pytest.approx(300.0 * 0.85, rel=1e-2)
    
    def test_validate_data_quality(self):
        """Test data quality validation"""
        invalid_data = [
            {"symbol": "", "name": "Test", "price": 100.0},  # Empty symbol
            {"symbol": "TEST", "name": "", "price": 100.0},  # Empty name
            {"symbol": "TEST", "name": "Test", "price": -100.0},  # Negative price
            {"symbol": "TEST", "name": "Test", "price": "invalid"},  # Invalid price type
        ]
        
        quality_score = self.cleaner.validate_data_quality(invalid_data)
        assert 0 <= quality_score <= 100
        assert quality_score < 50  # Should be low due to invalid data


class TestDataTransformer:
    """Test data transformation functionality"""
    
    def setup_method(self):
        """Set up test data"""
        self.transformer = DataTransformer()
        self.sample_data = [
            {
                "symbol": "AAPL",
                "price": 150.0,
                "shares_outstanding": 1000000000,
                "date": "2024-01-01"
            },
            {
                "symbol": "MSFT",
                "price": 300.0,
                "shares_outstanding": 750000000,
                "date": "2024-01-01"
            }
        ]
    
    def test_calculate_market_cap(self):
        """Test market capitalization calculation"""
        transformed_data = self.transformer.calculate_market_cap(self.sample_data)
        
        for item in transformed_data:
            expected_market_cap = item["price"] * item["shares_outstanding"]
            assert item["market_cap"] == expected_market_cap
    
    def test_calculate_performance_metrics(self):
        """Test performance metrics calculation"""
        price_data = [
            {"symbol": "AAPL", "price": 100.0, "date": "2024-01-01"},
            {"symbol": "AAPL", "price": 110.0, "date": "2024-01-02"},
            {"symbol": "AAPL", "price": 105.0, "date": "2024-01-03"},
        ]
        
        performance_data = self.transformer.calculate_performance_metrics(price_data)
        
        # Check that performance metrics are calculated
        assert "daily_return" in performance_data[1]
        assert "volatility" in performance_data[2]
        assert performance_data[1]["daily_return"] == pytest.approx(0.1, rel=1e-2)
    
    def test_calculate_volatility(self):
        """Test volatility calculation"""
        returns = [0.01, 0.02, -0.01, 0.03, -0.02, 0.01, 0.02, -0.01]
        volatility = self.transformer.calculate_volatility(returns)
        
        assert volatility > 0
        assert isinstance(volatility, float)


class TestSecurityModel:
    """Test Security model functionality"""
    
    def test_security_creation(self):
        """Test security model creation"""
        security = Security(
            symbol="AAPL",
            name="Apple Inc.",
            exchange="NASDAQ",
            currency="USD",
            sector="Technology",
            industry="Consumer Electronics",
            country="USA",
            market_cap=3000000000000.0,
            is_active=True
        )
        
        assert security.symbol == "AAPL"
        assert security.name == "Apple Inc."
        assert security.is_active is True
        assert security.created_at is not None
    
    def test_security_schema_validation(self):
        """Test security schema validation"""
        # Valid data
        valid_data = {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "exchange": "NASDAQ",
            "currency": "USD",
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "country": "USA",
            "market_cap": 3000000000000.0
        }
        
        security_create = SecurityCreate(**valid_data)
        assert security_create.symbol == "AAPL"
        
        # Invalid data (missing required field)
        invalid_data = {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            # Missing exchange
            "currency": "USD"
        }
        
        with pytest.raises(ValueError):
            SecurityCreate(**invalid_data)
    
    def test_security_update_schema(self):
        """Test security update schema"""
        update_data = {
            "name": "Apple Inc. Updated",
            "market_cap": 3100000000000.0
        }
        
        security_update = SecurityUpdate(**update_data)
        assert security_update.name == "Apple Inc. Updated"
        assert security_update.market_cap == 3100000000000.0


class TestIndexCalculation:
    """Test index calculation functionality"""
    
    def setup_method(self):
        """Set up test data"""
        self.sample_constituents = [
            {"symbol": "AAPL", "price": 150.0, "shares": 1000000, "market_cap": 150000000},
            {"symbol": "MSFT", "price": 300.0, "shares": 500000, "market_cap": 150000000},
            {"symbol": "GOOGL", "price": 2500.0, "shares": 100000, "market_cap": 250000000}
        ]
    
    def test_equal_weight_calculation(self):
        """Test equal weight index calculation"""
        from app.calculation.index_engine import IndexEngine
        
        engine = IndexEngine()
        weights = engine.calculate_equal_weights(self.sample_constituents)
        
        # All weights should be equal (1/3 ≈ 0.333)
        expected_weight = 1.0 / len(self.sample_constituents)
        for weight in weights:
            assert weight == pytest.approx(expected_weight, rel=1e-2)
    
    def test_market_cap_weight_calculation(self):
        """Test market cap weight index calculation"""
        from app.calculation.index_engine import IndexEngine
        
        engine = IndexEngine()
        weights = engine.calculate_market_cap_weights(self.sample_constituents)
        
        # Weights should sum to 1.0
        assert sum(weights) == pytest.approx(1.0, rel=1e-2)
        
        # GOOGL should have the highest weight (highest market cap)
        assert weights[2] > weights[0]  # GOOGL > AAPL
        assert weights[2] > weights[1]  # GOOGL > MSFT
    
    def test_price_weight_calculation(self):
        """Test price weight index calculation"""
        from app.calculation.index_engine import IndexEngine
        
        engine = IndexEngine()
        weights = engine.calculate_price_weights(self.sample_constituents)
        
        # Weights should sum to 1.0
        assert sum(weights) == pytest.approx(1.0, rel=1e-2)
        
        # GOOGL should have the highest weight (highest price)
        assert weights[2] > weights[0]  # GOOGL > AAPL
        assert weights[2] > weights[1]  # GOOGL > MSFT
    
    def test_index_value_calculation(self):
        """Test index value calculation"""
        from app.calculation.index_engine import IndexEngine
        
        engine = IndexEngine()
        base_value = 1000.0
        
        index_value = engine.calculate_index_value(
            self.sample_constituents,
            weights=[0.33, 0.33, 0.34],
            base_value=base_value
        )
        
        assert index_value > 0
        assert isinstance(index_value, float)


class TestDataValidation:
    """Test data validation functionality"""
    
    def test_security_data_validation(self):
        """Test security data validation"""
        from app.ingestion.base import BaseIngestor
        
        # Valid data
        valid_data = {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "exchange": "NASDAQ",
            "currency": "USD",
            "sector": "Technology",
            "market_cap": 3000000000000.0
        }
        
        assert BaseIngestor.validate_security_data(valid_data) is True
        
        # Invalid data
        invalid_data = {
            "symbol": "",  # Empty symbol
            "name": "Apple Inc.",
            "exchange": "NASDAQ",
            "currency": "USD",
            "sector": "Technology",
            "market_cap": -1000.0  # Negative market cap
        }
        
        assert BaseIngestor.validate_security_data(invalid_data) is False
    
    def test_price_data_validation(self):
        """Test price data validation"""
        from app.ingestion.base import BaseIngestor
        
        # Valid data
        valid_data = {
            "symbol": "AAPL",
            "date": "2024-01-01",
            "open_price": 150.0,
            "high_price": 155.0,
            "low_price": 148.0,
            "close_price": 152.0,
            "volume": 1000000
        }
        
        assert BaseIngestor.validate_price_data(valid_data) is True
        
        # Invalid data
        invalid_data = {
            "symbol": "AAPL",
            "date": "invalid-date",
            "open_price": 150.0,
            "high_price": 155.0,
            "low_price": 148.0,
            "close_price": 152.0,
            "volume": -1000  # Negative volume
        }
        
        assert BaseIngestor.validate_price_data(invalid_data) is False
