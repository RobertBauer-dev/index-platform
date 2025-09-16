"""
Unit tests for data processing functionality
"""
import pytest
from unittest.mock import Mock, patch
import pandas as pd
from datetime import datetime, date

from app.processing.data_cleaner import DataCleaner
from app.processing.data_transformer import DataTransformer
from app.processing.etl_pipeline import ETLPipeline


class TestDataCleaner:
    """Test data cleaning functionality"""
    
    def setup_method(self):
        """Set up test data"""
        self.cleaner = DataCleaner()
        self.sample_securities = [
            {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "exchange": "NASDAQ",
                "currency": "USD",
                "sector": "Technology",
                "market_cap": 3000000000000.0,
                "price": 150.0
            },
            {
                "symbol": "AAPL",  # Duplicate
                "name": "Apple Inc.",
                "exchange": "NASDAQ",
                "currency": "USD",
                "sector": "Technology",
                "market_cap": 3000000000000.0,
                "price": 151.0
            },
            {
                "symbol": "MSFT",
                "name": "Microsoft Corp.",
                "exchange": "NASDAQ",
                "currency": "EUR",  # Different currency
                "sector": "Technology",
                "market_cap": 2800000000000.0,
                "price": 300.0
            },
            {
                "symbol": "INVALID",
                "name": "",  # Empty name
                "exchange": "NASDAQ",
                "currency": "USD",
                "sector": "Technology",
                "market_cap": -1000.0,  # Negative market cap
                "price": 0.0  # Zero price
            }
        ]
    
    def test_remove_duplicates(self):
        """Test duplicate removal"""
        cleaned_data = self.cleaner.remove_duplicates(self.sample_securities, key="symbol")
        
        assert len(cleaned_data) == 3  # Should remove one duplicate
        symbols = [item["symbol"] for item in cleaned_data]
        assert "AAPL" in symbols
        assert "MSFT" in symbols
        assert "INVALID" in symbols
        assert symbols.count("AAPL") == 1  # Only one AAPL
    
    def test_remove_duplicates_custom_key(self):
        """Test duplicate removal with custom key"""
        data = [
            {"id": 1, "name": "Test1", "value": 100},
            {"id": 2, "name": "Test1", "value": 200},  # Same name, different id
            {"id": 1, "name": "Test2", "value": 300}   # Same id, different name
        ]
        
        # Remove by name
        cleaned_by_name = self.cleaner.remove_duplicates(data, key="name")
        assert len(cleaned_by_name) == 2
        
        # Remove by id
        cleaned_by_id = self.cleaner.remove_duplicates(data, key="id")
        assert len(cleaned_by_id) == 2
    
    def test_harmonize_currencies(self):
        """Test currency harmonization"""
        with patch.object(self.cleaner, 'get_exchange_rate', return_value=0.85):
            harmonized_data = self.cleaner.harmonize_currencies(
                self.sample_securities, target_currency="USD"
            )
            
            # All currencies should be USD
            for item in harmonized_data:
                assert item["currency"] == "USD"
            
            # EUR price should be converted
            msft_item = next(item for item in harmonized_data if item["symbol"] == "MSFT")
            assert msft_item["price"] == pytest.approx(300.0 * 0.85, rel=1e-2)
            assert msft_item["market_cap"] == pytest.approx(2800000000000.0 * 0.85, rel=1e-2)
    
    def test_normalize_timezones(self):
        """Test timezone normalization"""
        data_with_timezones = [
            {
                "symbol": "AAPL",
                "date": "2024-01-01T10:00:00+00:00",  # UTC
                "price": 150.0
            },
            {
                "symbol": "MSFT",
                "date": "2024-01-01T05:00:00-05:00",  # EST
                "price": 300.0
            }
        ]
        
        normalized_data = self.cleaner.normalize_timezones(
            data_with_timezones, target_timezone="UTC"
        )
        
        for item in normalized_data:
            # All dates should be in UTC
            assert "T" in item["date"]
            assert item["date"].endswith("+00:00") or item["date"].endswith("Z")
    
    def test_validate_data_quality(self):
        """Test data quality validation"""
        quality_score = self.cleaner.validate_data_quality(self.sample_securities)
        
        assert 0 <= quality_score <= 100
        assert quality_score < 100  # Should be less than perfect due to invalid data
    
    def test_validate_data_quality_perfect_data(self):
        """Test data quality validation with perfect data"""
        perfect_data = [
            {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "exchange": "NASDAQ",
                "currency": "USD",
                "sector": "Technology",
                "market_cap": 3000000000000.0,
                "price": 150.0
            },
            {
                "symbol": "MSFT",
                "name": "Microsoft Corp.",
                "exchange": "NASDAQ",
                "currency": "USD",
                "sector": "Technology",
                "market_cap": 2800000000000.0,
                "price": 300.0
            }
        ]
        
        quality_score = self.cleaner.validate_data_quality(perfect_data)
        assert quality_score == 100  # Perfect data should score 100
    
    def test_handle_missing_values(self):
        """Test handling of missing values"""
        data_with_missing = [
            {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "exchange": "NASDAQ",
                "currency": "USD",
                "sector": "Technology",
                "market_cap": 3000000000000.0,
                "price": 150.0,
                "dividend": None  # Missing value
            },
            {
                "symbol": "MSFT",
                "name": "Microsoft Corp.",
                "exchange": "NASDAQ",
                "currency": "USD",
                "sector": "Technology",
                "market_cap": 2800000000000.0,
                "price": 300.0,
                "dividend": 2.5
            }
        ]
        
        cleaned_data = self.cleaner.handle_missing_values(
            data_with_missing, default_values={"dividend": 0.0}
        )
        
        # Missing dividend should be filled with default value
        aapl_item = next(item for item in cleaned_data if item["symbol"] == "AAPL")
        assert aapl_item["dividend"] == 0.0
        
        # Existing dividend should remain unchanged
        msft_item = next(item for item in cleaned_data if item["symbol"] == "MSFT")
        assert msft_item["dividend"] == 2.5
    
    def test_validate_numeric_ranges(self):
        """Test validation of numeric ranges"""
        data_with_invalid_ranges = [
            {
                "symbol": "AAPL",
                "price": 150.0,  # Valid
                "volume": 1000000,  # Valid
                "market_cap": 3000000000000.0  # Valid
            },
            {
                "symbol": "INVALID",
                "price": -100.0,  # Invalid: negative price
                "volume": -1000,  # Invalid: negative volume
                "market_cap": 0.0  # Invalid: zero market cap
            }
        ]
        
        validation_rules = {
            "price": {"min": 0.01, "max": 10000.0},
            "volume": {"min": 0, "max": 10000000000},
            "market_cap": {"min": 1000000, "max": 10000000000000}
        }
        
        valid_data = self.cleaner.validate_numeric_ranges(
            data_with_invalid_ranges, validation_rules
        )
        
        # Should filter out invalid data
        assert len(valid_data) == 1
        assert valid_data[0]["symbol"] == "AAPL"


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
        
        # AAPL: 150 * 1B = 150B
        aapl_item = next(item for item in transformed_data if item["symbol"] == "AAPL")
        assert aapl_item["market_cap"] == 150000000000
        
        # MSFT: 300 * 750M = 225B
        msft_item = next(item for item in transformed_data if item["symbol"] == "MSFT")
        assert msft_item["market_cap"] == 225000000000
    
    def test_calculate_performance_metrics(self):
        """Test performance metrics calculation"""
        price_data = [
            {"symbol": "AAPL", "price": 100.0, "date": "2024-01-01"},
            {"symbol": "AAPL", "price": 110.0, "date": "2024-01-02"},
            {"symbol": "AAPL", "price": 105.0, "date": "2024-01-03"},
            {"symbol": "AAPL", "price": 115.0, "date": "2024-01-04"}
        ]
        
        performance_data = self.transformer.calculate_performance_metrics(price_data)
        
        # Check that performance metrics are calculated
        assert len(performance_data) == 4
        
        # First item should not have daily return
        assert "daily_return" not in performance_data[0]
        
        # Second item should have daily return
        assert "daily_return" in performance_data[1]
        assert performance_data[1]["daily_return"] == pytest.approx(0.10, rel=1e-2)
        
        # Last item should have volatility
        assert "volatility" in performance_data[-1]
    
    def test_calculate_volatility(self):
        """Test volatility calculation"""
        returns = [0.01, 0.02, -0.01, 0.03, -0.02, 0.01, 0.02, -0.01]
        
        volatility = self.transformer.calculate_volatility(returns)
        
        assert volatility > 0
        assert isinstance(volatility, float)
        assert volatility < 1.0  # Should be reasonable volatility
    
    def test_calculate_beta(self):
        """Test beta calculation"""
        stock_returns = [0.01, 0.02, -0.01, 0.03, -0.02]
        market_returns = [0.005, 0.015, -0.005, 0.025, -0.015]
        
        beta = self.transformer.calculate_beta(stock_returns, market_returns)
        
        assert isinstance(beta, float)
        # Beta can be positive or negative depending on correlation
    
    def test_calculate_sharpe_ratio(self):
        """Test Sharpe ratio calculation"""
        returns = [0.01, 0.02, -0.01, 0.03, -0.02, 0.01, 0.02, -0.01]
        risk_free_rate = 0.02  # 2% annual
        
        sharpe_ratio = self.transformer.calculate_sharpe_ratio(returns, risk_free_rate)
        
        assert isinstance(sharpe_ratio, float)
    
    def test_calculate_rsi(self):
        """Test RSI calculation"""
        prices = [100, 102, 101, 103, 105, 104, 106, 108, 107, 109]
        
        rsi = self.transformer.calculate_rsi(prices, period=5)
        
        assert isinstance(rsi, float)
        assert 0 <= rsi <= 100  # RSI should be between 0 and 100
    
    def test_calculate_moving_averages(self):
        """Test moving average calculations"""
        prices = [100, 102, 101, 103, 105, 104, 106, 108, 107, 109]
        
        sma_5 = self.transformer.calculate_simple_moving_average(prices, period=5)
        ema_5 = self.transformer.calculate_exponential_moving_average(prices, period=5)
        
        assert isinstance(sma_5, float)
        assert isinstance(ema_5, float)
        assert sma_5 > 0
        assert ema_5 > 0
    
    def test_calculate_bollinger_bands(self):
        """Test Bollinger Bands calculation"""
        prices = [100, 102, 101, 103, 105, 104, 106, 108, 107, 109]
        
        bands = self.transformer.calculate_bollinger_bands(prices, period=5, std_dev=2)
        
        assert "upper_band" in bands
        assert "middle_band" in bands
        assert "lower_band" in bands
        
        assert bands["upper_band"] > bands["middle_band"]
        assert bands["middle_band"] > bands["lower_band"]
    
    def test_calculate_macd(self):
        """Test MACD calculation"""
        prices = [100, 102, 101, 103, 105, 104, 106, 108, 107, 109, 111, 110, 112, 114, 113]
        
        macd = self.transformer.calculate_macd(prices)
        
        assert "macd_line" in macd
        assert "signal_line" in macd
        assert "histogram" in macd
        
        assert isinstance(macd["macd_line"], float)
        assert isinstance(macd["signal_line"], float)
        assert isinstance(macd["histogram"], float)
    
    def test_aggregate_data_by_timeframe(self):
        """Test data aggregation by timeframe"""
        daily_data = [
            {"date": "2024-01-01", "price": 100.0, "volume": 1000},
            {"date": "2024-01-02", "price": 102.0, "volume": 1200},
            {"date": "2024-01-03", "price": 101.0, "volume": 1100},
            {"date": "2024-01-04", "price": 103.0, "volume": 1300},
            {"date": "2024-01-05", "price": 105.0, "volume": 1400}
        ]
        
        weekly_data = self.transformer.aggregate_data_by_timeframe(
            daily_data, timeframe="weekly"
        )
        
        assert len(weekly_data) == 1  # One week of data
        assert "price" in weekly_data[0]
        assert "volume" in weekly_data[0]
        assert "date" in weekly_data[0]
    
    def test_calculate_sector_performance(self):
        """Test sector performance calculation"""
        sector_data = {
            "Technology": [
                {"symbol": "AAPL", "return": 0.10},
                {"symbol": "MSFT", "return": 0.08}
            ],
            "Healthcare": [
                {"symbol": "JNJ", "return": 0.05},
                {"symbol": "PFE", "return": 0.03}
            ]
        }
        
        sector_performance = self.transformer.calculate_sector_performance(sector_data)
        
        assert "Technology" in sector_performance
        assert "Healthcare" in sector_performance
        
        # Technology should have higher average return
        assert sector_performance["Technology"]["average_return"] > sector_performance["Healthcare"]["average_return"]


class TestETLPipeline:
    """Test ETL pipeline functionality"""
    
    def setup_method(self):
        """Set up test data"""
        self.pipeline = ETLPipeline()
        self.cleaner = DataCleaner()
        self.transformer = DataTransformer()
    
    def test_full_etl_pipeline(self):
        """Test complete ETL pipeline"""
        raw_data = [
            {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "price": 150.0,
                "currency": "USD",
                "date": "2024-01-01",
                "volume": 1000000
            },
            {
                "symbol": "AAPL",  # Duplicate
                "name": "Apple Inc.",
                "price": 151.0,
                "currency": "USD",
                "date": "2024-01-01",
                "volume": 1000000
            },
            {
                "symbol": "MSFT",
                "name": "Microsoft Corp.",
                "price": 300.0,
                "currency": "EUR",
                "date": "2024-01-01",
                "volume": 500000
            }
        ]
        
        # Run ETL pipeline
        processed_data = self.pipeline.run_pipeline(raw_data)
        
        # Should remove duplicates
        assert len(processed_data) == 2
        
        # Should harmonize currencies
        for item in processed_data:
            assert item["currency"] == "USD"
        
        # Should have calculated metrics
        for item in processed_data:
            assert "market_cap" in item or "processed_at" in item
    
    def test_pipeline_with_validation(self):
        """Test ETL pipeline with data validation"""
        invalid_data = [
            {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "price": 150.0,
                "currency": "USD",
                "date": "2024-01-01",
                "volume": 1000000
            },
            {
                "symbol": "INVALID",
                "name": "",  # Invalid: empty name
                "price": -100.0,  # Invalid: negative price
                "currency": "USD",
                "date": "2024-01-01",
                "volume": -1000  # Invalid: negative volume
            }
        ]
        
        # Run pipeline with validation
        processed_data = self.pipeline.run_pipeline(
            invalid_data, validate=True, strict=True
        )
        
        # Should filter out invalid data
        assert len(processed_data) == 1
        assert processed_data[0]["symbol"] == "AAPL"
    
    def test_pipeline_error_handling(self):
        """Test ETL pipeline error handling"""
        # Test with empty data
        processed_data = self.pipeline.run_pipeline([])
        assert processed_data == []
        
        # Test with malformed data
        malformed_data = [
            {"invalid": "data"},
            {"another": "invalid", "structure": "here"}
        ]
        
        # Should handle gracefully
        processed_data = self.pipeline.run_pipeline(malformed_data, strict=False)
        assert isinstance(processed_data, list)
    
    def test_pipeline_performance(self):
        """Test ETL pipeline performance with large dataset"""
        # Create large dataset
        large_data = []
        for i in range(1000):
            large_data.append({
                "symbol": f"STOCK{i:04d}",
                "name": f"Company {i}",
                "price": 100.0 + i,
                "currency": "USD",
                "date": "2024-01-01",
                "volume": 1000000 + i
            })
        
        # Should handle large datasets efficiently
        import time
        start_time = time.time()
        
        processed_data = self.pipeline.run_pipeline(large_data)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete within reasonable time (< 5 seconds)
        assert execution_time < 5.0
        assert len(processed_data) == len(large_data)
