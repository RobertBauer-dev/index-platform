"""
Unit tests for index calculation functionality
"""
import pytest
from datetime import datetime, date
from unittest.mock import Mock, patch
import numpy as np

from app.calculation.index_engine import IndexEngine
from app.db.models import IndexDefinition, Security, IndexValue, IndexConstituent
from app.db.schemas import IndexDefinitionCreate, IndexValueCreate


class TestIndexEngine:
    """Test index calculation engine"""
    
    def setup_method(self):
        """Set up test data"""
        self.engine = IndexEngine()
        self.sample_securities = [
            {
                "id": 1,
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "price": 150.0,
                "shares_outstanding": 1000000000,
                "market_cap": 150000000000,
                "sector": "Technology"
            },
            {
                "id": 2,
                "symbol": "MSFT",
                "name": "Microsoft Corp.",
                "price": 300.0,
                "shares_outstanding": 750000000,
                "market_cap": 225000000000,
                "sector": "Technology"
            },
            {
                "id": 3,
                "symbol": "GOOGL",
                "name": "Alphabet Inc.",
                "price": 2500.0,
                "shares_outstanding": 100000000,
                "market_cap": 250000000000,
                "sector": "Technology"
            }
        ]
    
    def test_equal_weight_calculation(self):
        """Test equal weight index calculation"""
        weights = self.engine.calculate_equal_weights(self.sample_securities)
        
        # All weights should be equal
        expected_weight = 1.0 / len(self.sample_securities)
        for weight in weights:
            assert weight == pytest.approx(expected_weight, rel=1e-2)
        
        # Weights should sum to 1.0
        assert sum(weights) == pytest.approx(1.0, rel=1e-2)
    
    def test_market_cap_weight_calculation(self):
        """Test market cap weight calculation"""
        weights = self.engine.calculate_market_cap_weights(self.sample_securities)
        
        # Weights should sum to 1.0
        assert sum(weights) == pytest.approx(1.0, rel=1e-2)
        
        # GOOGL should have highest weight (highest market cap)
        assert weights[2] > weights[1]  # GOOGL > MSFT
        assert weights[2] > weights[0]  # GOOGL > AAPL
        
        # MSFT should have second highest weight
        assert weights[1] > weights[0]  # MSFT > AAPL
    
    def test_price_weight_calculation(self):
        """Test price weight calculation"""
        weights = self.engine.calculate_price_weights(self.sample_securities)
        
        # Weights should sum to 1.0
        assert sum(weights) == pytest.approx(1.0, rel=1e-2)
        
        # GOOGL should have highest weight (highest price)
        assert weights[2] > weights[1]  # GOOGL > MSFT
        assert weights[2] > weights[0]  # GOOGL > AAPL
        
        # MSFT should have second highest weight
        assert weights[1] > weights[0]  # MSFT > AAPL
    
    def test_esg_weight_calculation(self):
        """Test ESG weight calculation"""
        # Add ESG scores to securities
        securities_with_esg = [
            {**sec, "esg_score": 8.5} for sec in self.sample_securities[:2]
        ] + [{**self.sample_securities[2], "esg_score": 7.0}]
        
        weights = self.engine.calculate_esg_weights(securities_with_esg)
        
        # Weights should sum to 1.0
        assert sum(weights) == pytest.approx(1.0, rel=1e-2)
        
        # AAPL and MSFT should have higher weights (higher ESG scores)
        assert weights[0] > weights[2]  # AAPL > GOOGL
        assert weights[1] > weights[2]  # MSFT > GOOGL
    
    def test_index_value_calculation(self):
        """Test index value calculation"""
        base_value = 1000.0
        weights = [0.33, 0.33, 0.34]
        
        index_value = self.engine.calculate_index_value(
            self.sample_securities,
            weights,
            base_value
        )
        
        assert index_value > 0
        assert isinstance(index_value, float)
        assert index_value == pytest.approx(base_value, rel=1e-2)
    
    def test_performance_calculation(self):
        """Test performance metrics calculation"""
        # Historical prices
        historical_prices = [
            {"date": "2024-01-01", "price": 100.0},
            {"date": "2024-01-02", "price": 105.0},
            {"date": "2024-01-03", "price": 102.0},
            {"date": "2024-01-04", "price": 108.0},
            {"date": "2024-01-05", "price": 110.0}
        ]
        
        performance = self.engine.calculate_performance_metrics(historical_prices)
        
        assert "total_return" in performance
        assert "volatility" in performance
        assert "sharpe_ratio" in performance
        assert "max_drawdown" in performance
        
        # Total return should be 10% (100 to 110)
        assert performance["total_return"] == pytest.approx(0.10, rel=1e-2)
    
    def test_rebalancing_logic(self):
        """Test index rebalancing logic"""
        # Create index definition
        index_def = Mock()
        index_def.rebalance_frequency = "monthly"
        index_def.max_constituents = 2
        
        # Test rebalancing needed
        last_rebalance = datetime(2024, 1, 1)
        current_date = datetime(2024, 2, 1)
        
        needs_rebalance = self.engine.needs_rebalancing(
            index_def, last_rebalance, current_date
        )
        assert needs_rebalance is True
        
        # Test rebalancing not needed
        current_date = datetime(2024, 1, 15)
        needs_rebalance = self.engine.needs_rebalancing(
            index_def, last_rebalance, current_date
        )
        assert needs_rebalance is False
    
    def test_constituent_selection(self):
        """Test constituent selection logic"""
        # Create index definition with filters
        index_def = Mock()
        index_def.sectors = ["Technology"]
        index_def.min_market_cap = 100000000000  # 100B
        index_def.max_market_cap = 500000000000  # 500B
        index_def.max_constituents = 2
        
        # Filter securities
        filtered_securities = self.engine.select_constituents(
            self.sample_securities, index_def
        )
        
        # Should filter by market cap and limit to max_constituents
        assert len(filtered_securities) <= index_def.max_constituents
        
        # All selected securities should meet criteria
        for security in filtered_securities:
            assert index_def.min_market_cap <= security["market_cap"] <= index_def.max_market_cap
            assert security["sector"] in index_def.sectors
    
    def test_dividend_adjustment(self):
        """Test dividend adjustment calculation"""
        # Test dividend adjustment
        price_before = 100.0
        dividend = 2.0
        split_ratio = 1.0
        
        adjusted_price = self.engine.calculate_dividend_adjustment(
            price_before, dividend, split_ratio
        )
        
        assert adjusted_price == pytest.approx(98.0, rel=1e-2)
    
    def test_split_adjustment(self):
        """Test stock split adjustment calculation"""
        # Test 2:1 split
        price_before = 100.0
        split_ratio = 2.0
        
        adjusted_price = self.engine.calculate_split_adjustment(price_before, split_ratio)
        
        assert adjusted_price == pytest.approx(50.0, rel=1e-2)
    
    def test_volatility_calculation(self):
        """Test volatility calculation"""
        returns = [0.01, 0.02, -0.01, 0.03, -0.02, 0.01, 0.02, -0.01]
        
        volatility = self.engine.calculate_volatility(returns)
        
        assert volatility > 0
        assert isinstance(volatility, float)
        assert volatility < 1.0  # Should be reasonable volatility
    
    def test_sharpe_ratio_calculation(self):
        """Test Sharpe ratio calculation"""
        returns = [0.01, 0.02, -0.01, 0.03, -0.02, 0.01, 0.02, -0.01]
        risk_free_rate = 0.02  # 2% annual
        
        sharpe_ratio = self.engine.calculate_sharpe_ratio(returns, risk_free_rate)
        
        assert isinstance(sharpe_ratio, float)
        # Sharpe ratio can be positive or negative depending on returns
    
    def test_max_drawdown_calculation(self):
        """Test maximum drawdown calculation"""
        prices = [100, 105, 102, 108, 95, 98, 110, 115]
        
        max_drawdown = self.engine.calculate_max_drawdown(prices)
        
        assert max_drawdown >= 0
        assert max_drawdown <= 1.0
        assert isinstance(max_drawdown, float)
    
    def test_correlation_calculation(self):
        """Test correlation calculation between securities"""
        returns_a = [0.01, 0.02, -0.01, 0.03, -0.02]
        returns_b = [0.02, 0.01, -0.02, 0.04, -0.01]
        
        correlation = self.engine.calculate_correlation(returns_a, returns_b)
        
        assert -1.0 <= correlation <= 1.0
        assert isinstance(correlation, float)
    
    def test_sector_allocation(self):
        """Test sector allocation calculation"""
        securities_by_sector = {
            "Technology": [
                {"market_cap": 100000000000},
                {"market_cap": 200000000000}
            ],
            "Healthcare": [
                {"market_cap": 150000000000}
            ]
        }
        
        sector_allocation = self.engine.calculate_sector_allocation(securities_by_sector)
        
        total_market_cap = sum(
            sum(sec["market_cap"] for sec in securities)
            for securities in securities_by_sector.values()
        )
        
        # Allocations should sum to 1.0
        assert sum(sector_allocation.values()) == pytest.approx(1.0, rel=1e-2)
        
        # Technology should have higher allocation (300B vs 150B)
        assert sector_allocation["Technology"] > sector_allocation["Healthcare"]
    
    def test_esg_filtering(self):
        """Test ESG-based filtering"""
        securities_with_esg = [
            {**sec, "esg_score": 8.5} for sec in self.sample_securities[:2]
        ] + [{**self.sample_securities[2], "esg_score": 6.0}]
        
        esg_criteria = {"min_esg_score": 7.0}
        
        filtered_securities = self.engine.apply_esg_filters(
            securities_with_esg, esg_criteria
        )
        
        # Should filter out GOOGL (ESG score 6.0 < 7.0)
        assert len(filtered_securities) == 2
        
        # All remaining securities should meet ESG criteria
        for security in filtered_securities:
            assert security["esg_score"] >= esg_criteria["min_esg_score"]
    
    def test_backtesting_simulation(self):
        """Test backtesting simulation"""
        # Mock historical data
        historical_data = {
            "2024-01-01": [{"symbol": "AAPL", "price": 100.0}],
            "2024-01-02": [{"symbol": "AAPL", "price": 105.0}],
            "2024-01-03": [{"symbol": "AAPL", "price": 102.0}]
        }
        
        index_definition = Mock()
        index_definition.weighting_method = "equal_weight"
        
        backtest_results = self.engine.run_backtest(
            index_definition, historical_data, "2024-01-01", "2024-01-03"
        )
        
        assert "index_values" in backtest_results
        assert "performance_metrics" in backtest_results
        assert "constituents_history" in backtest_results
        
        # Should have index values for each date
        assert len(backtest_results["index_values"]) == 3
        
        # Performance metrics should be calculated
        assert "total_return" in backtest_results["performance_metrics"]
        assert "volatility" in backtest_results["performance_metrics"]
    
    def test_error_handling(self):
        """Test error handling in index calculations"""
        # Test with empty securities list
        with pytest.raises(ValueError):
            self.engine.calculate_equal_weights([])
        
        # Test with invalid weights
        with pytest.raises(ValueError):
            self.engine.calculate_index_value(
                self.sample_securities, [0.5, 0.5], 1000.0
            )  # Wrong number of weights
        
        # Test with negative prices
        invalid_securities = [
            {**self.sample_securities[0], "price": -100.0}
        ]
        
        with pytest.raises(ValueError):
            self.engine.calculate_market_cap_weights(invalid_securities)
    
    def test_performance_optimization(self):
        """Test performance optimization for large datasets"""
        # Create large dataset
        large_securities = []
        for i in range(1000):
            large_securities.append({
                "id": i,
                "symbol": f"STOCK{i:04d}",
                "price": 100.0 + i,
                "market_cap": 1000000000 + (i * 1000000),
                "sector": "Technology" if i % 2 == 0 else "Healthcare"
            })
        
        # Should handle large datasets efficiently
        import time
        start_time = time.time()
        
        weights = self.engine.calculate_market_cap_weights(large_securities)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete within reasonable time (< 1 second)
        assert execution_time < 1.0
        assert len(weights) == len(large_securities)
        assert sum(weights) == pytest.approx(1.0, rel=1e-2)
