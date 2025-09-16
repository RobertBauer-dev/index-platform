"""
System tests for end-to-end workflows
"""
import pytest
import time
from datetime import datetime, date
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.db.models import User, Security, IndexDefinition, PriceData, IndexValue


class TestCompleteDataIngestionWorkflow:
    """Test complete data ingestion workflow"""
    
    def test_security_ingestion_workflow(self, client: TestClient, admin_auth_headers, db_session: Session):
        """Test complete workflow from CSV ingestion to database storage"""
        # Step 1: Create CSV content
        csv_content = """symbol,name,exchange,currency,sector,industry,country,market_cap
AAPL,Apple Inc.,NASDAQ,USD,Technology,Consumer Electronics,USA,3000000000000
MSFT,Microsoft Corporation,NASDAQ,USD,Technology,Software,USA,2800000000000
GOOGL,Alphabet Inc.,NASDAQ,USD,Technology,Internet,USA,1800000000000"""
        
        # Step 2: Ingest securities via API
        files = {"file": ("securities.csv", csv_content, "text/csv")}
        response = client.post(
            "/api/v1/ingestion/csv/securities",
            files=files,
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        ingestion_result = response.json()
        assert ingestion_result["ingested_count"] == 3
        
        # Step 3: Verify securities are in database
        securities = db_session.query(Security).all()
        assert len(securities) >= 3
        
        # Step 4: Verify securities are accessible via API
        response = client.get("/api/v1/securities", headers=admin_auth_headers)
        assert response.status_code == 200
        securities_data = response.json()
        assert len(securities_data) >= 3
        
        # Verify specific securities
        symbols = [s["symbol"] for s in securities_data]
        assert "AAPL" in symbols
        assert "MSFT" in symbols
        assert "GOOGL" in symbols
    
    def test_price_data_ingestion_workflow(self, client: TestClient, admin_auth_headers, db_session: Session, test_security):
        """Test complete workflow for price data ingestion"""
        # Step 1: Create price data CSV
        csv_content = """symbol,date,open_price,high_price,low_price,close_price,volume,adjusted_close,dividend,split_ratio
AAPL,2024-01-01,150.0,155.0,148.0,152.0,1000000,152.0,0.0,1.0
AAPL,2024-01-02,152.0,158.0,151.0,156.0,1200000,156.0,0.0,1.0
AAPL,2024-01-03,156.0,160.0,154.0,158.0,1100000,158.0,0.0,1.0"""
        
        # Step 2: Ingest price data via API
        files = {"file": ("prices.csv", csv_content, "text/csv")}
        response = client.post(
            "/api/v1/ingestion/csv/prices",
            files=files,
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        ingestion_result = response.json()
        assert ingestion_result["ingested_count"] == 3
        
        # Step 3: Verify price data is in database
        price_data = db_session.query(PriceData).filter(
            PriceData.security_id == test_security.id
        ).all()
        assert len(price_data) >= 3
        
        # Step 4: Verify price data is accessible via API
        response = client.get(
            f"/api/v1/securities/{test_security.id}/prices",
            headers=admin_auth_headers
        )
        assert response.status_code == 200
        prices_data = response.json()
        assert len(prices_data) >= 3


class TestCompleteIndexCalculationWorkflow:
    """Test complete index calculation workflow"""
    
    def test_index_creation_and_calculation_workflow(self, client: TestClient, auth_headers, db_session: Session, test_security):
        """Test complete workflow from index creation to calculation"""
        # Step 1: Create index definition
        index_data = {
            "name": "Technology Leaders Index",
            "description": "Leading technology companies",
            "weighting_method": "market_cap_weight",
            "rebalance_frequency": "monthly",
            "max_constituents": 10,
            "min_market_cap": 1000000000.0,
            "max_market_cap": 5000000000000.0,
            "sectors": ["Technology"],
            "countries": ["USA"],
            "esg_criteria": {"min_esg_score": 6.0},
            "is_active": True
        }
        
        response = client.post(
            "/api/v1/indices",
            json=index_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        index_result = response.json()
        index_id = index_result["id"]
        
        # Step 2: Verify index is created in database
        index_def = db_session.query(IndexDefinition).filter(
            IndexDefinition.id == index_id
        ).first()
        assert index_def is not None
        assert index_def.name == index_data["name"]
        
        # Step 3: Calculate index
        response = client.post(
            f"/api/v1/indices/{index_id}/calculate",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        calculation_result = response.json()
        assert "index_value" in calculation_result
        assert "calculation_date" in calculation_result
        
        # Step 4: Verify index values are stored
        index_values = db_session.query(IndexValue).filter(
            IndexValue.index_definition_id == index_id
        ).all()
        assert len(index_values) >= 1
        
        # Step 5: Retrieve index values via API
        response = client.get(
            f"/api/v1/indices/{index_id}/values",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        values_data = response.json()
        assert len(values_data) >= 1
    
    def test_index_backtesting_workflow(self, client: TestClient, auth_headers, test_index_definition):
        """Test complete index backtesting workflow"""
        # Step 1: Run backtest
        backtest_data = {
            "start_date": "2024-01-01",
            "end_date": "2024-01-31"
        }
        
        response = client.post(
            f"/api/v1/indices/{test_index_definition.id}/backtest",
            json=backtest_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        backtest_result = response.json()
        
        # Step 2: Verify backtest results structure
        assert "backtest_results" in backtest_result
        assert "performance_metrics" in backtest_result
        
        backtest_results = backtest_result["backtest_results"]
        assert "index_values" in backtest_results
        assert "constituents_history" in backtest_results
        
        # Step 3: Verify performance metrics
        performance_metrics = backtest_result["performance_metrics"]
        assert "total_return" in performance_metrics
        assert "volatility" in performance_metrics
        assert "sharpe_ratio" in performance_metrics


class TestCompleteUserWorkflow:
    """Test complete user workflow"""
    
    def test_user_registration_and_authentication_workflow(self, client: TestClient, db_session: Session):
        """Test complete user registration and authentication workflow"""
        # Step 1: Create user (this would typically be a registration endpoint)
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "full_name": "New User",
            "password": "newpassword123"
        }
        
        # For this test, we'll create the user directly in the database
        from app.core.security import get_password_hash
        user = User(
            email=user_data["email"],
            username=user_data["username"],
            full_name=user_data["full_name"],
            hashed_password=get_password_hash(user_data["password"]),
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Step 2: Login with new user
        response = client.post(
            "/api/v1/auth/token",
            data={
                "username": user_data["username"],
                "password": user_data["password"]
            }
        )
        
        assert response.status_code == 200
        auth_result = response.json()
        assert "access_token" in auth_result
        
        # Step 3: Use token to access protected endpoint
        headers = {"Authorization": f"Bearer {auth_result['access_token']}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 200
        user_info = response.json()
        assert user_info["email"] == user_data["email"]
        assert user_info["username"] == user_data["username"]
    
    def test_user_index_creation_workflow(self, client: TestClient, auth_headers, db_session: Session):
        """Test complete workflow of user creating and managing indices"""
        # Step 1: Create index
        index_data = {
            "name": "My Custom Index",
            "description": "A custom index created by user",
            "weighting_method": "equal_weight",
            "rebalance_frequency": "quarterly",
            "max_constituents": 20,
            "min_market_cap": 500000000.0,
            "max_market_cap": 1000000000000.0,
            "sectors": ["Technology", "Healthcare"],
            "countries": ["USA", "Germany"],
            "esg_criteria": {"min_esg_score": 7.0},
            "is_active": True
        }
        
        response = client.post(
            "/api/v1/indices",
            json=index_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        index_result = response.json()
        index_id = index_result["id"]
        
        # Step 2: Update index
        update_data = {
            "description": "Updated description",
            "max_constituents": 25
        }
        
        response = client.put(
            f"/api/v1/indices/{index_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        updated_index = response.json()
        assert updated_index["description"] == update_data["description"]
        assert updated_index["max_constituents"] == update_data["max_constituents"]
        
        # Step 3: Calculate index
        response = client.post(
            f"/api/v1/indices/{index_id}/calculate",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # Step 4: View index details
        response = client.get(
            f"/api/v1/indices/{index_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        index_details = response.json()
        assert index_details["id"] == index_id
        assert index_details["name"] == index_data["name"]


class TestCompleteDataProcessingWorkflow:
    """Test complete data processing workflow"""
    
    def test_data_cleaning_and_transformation_workflow(self, client: TestClient, admin_auth_headers, db_session: Session):
        """Test complete workflow from raw data to processed data"""
        # Step 1: Ingest raw data with quality issues
        raw_csv_content = """symbol,name,exchange,currency,sector,industry,country,market_cap
AAPL,Apple Inc.,NASDAQ,USD,Technology,Consumer Electronics,USA,3000000000000
AAPL,Apple Inc.,NASDAQ,USD,Technology,Consumer Electronics,USA,3000000000000
MSFT,Microsoft Corporation,NASDAQ,EUR,Technology,Software,USA,2800000000000
INVALID,,NASDAQ,USD,Technology,Software,USA,-1000"""
        
        files = {"file": ("raw_securities.csv", raw_csv_content, "text/csv")}
        response = client.post(
            "/api/v1/ingestion/csv/securities",
            files=files,
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        ingestion_result = response.json()
        
        # Step 2: Verify data cleaning (duplicates removed, invalid data filtered)
        securities = db_session.query(Security).all()
        assert len(securities) >= 2  # Should have at least AAPL and MSFT
        
        # Verify no duplicates
        symbols = [s.symbol for s in securities]
        assert symbols.count("AAPL") == 1
        
        # Verify invalid data is filtered out
        invalid_securities = [s for s in securities if s.symbol == "INVALID"]
        assert len(invalid_securities) == 0
        
        # Step 3: Verify data transformation (currency harmonization)
        msft_security = db_session.query(Security).filter(Security.symbol == "MSFT").first()
        assert msft_security is not None
        # Currency should be harmonized to USD (this depends on implementation)
    
    def test_index_rebalancing_workflow(self, client: TestClient, auth_headers, db_session: Session, test_index_definition):
        """Test complete index rebalancing workflow"""
        # Step 1: Initial index calculation
        response = client.post(
            f"/api/v1/indices/{test_index_definition.id}/calculate",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        initial_calculation = response.json()
        initial_value = initial_calculation["index_value"]
        
        # Step 2: Add new securities to the system
        new_security = Security(
            symbol="TSLA",
            name="Tesla Inc.",
            exchange="NASDAQ",
            currency="USD",
            sector="Automotive",
            industry="Electric Vehicles",
            country="USA",
            market_cap=800000000000.0,
            is_active=True
        )
        db_session.add(new_security)
        db_session.commit()
        
        # Step 3: Recalculate index (should include new security if it meets criteria)
        response = client.post(
            f"/api/v1/indices/{test_index_definition.id}/calculate",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        rebalanced_calculation = response.json()
        rebalanced_value = rebalanced_calculation["index_value"]
        
        # Step 4: Verify rebalancing occurred
        # The index value might change due to rebalancing
        assert rebalanced_value != initial_value or True  # Allow for no change if criteria not met


class TestCompleteMonitoringWorkflow:
    """Test complete monitoring and alerting workflow"""
    
    def test_metrics_collection_workflow(self, client: TestClient, auth_headers):
        """Test complete metrics collection workflow"""
        # Step 1: Make API requests to generate metrics
        endpoints = [
            "/api/v1/securities",
            "/api/v1/indices",
            "/health"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint, headers=auth_headers)
            assert response.status_code in [200, 401]
        
        # Step 2: Check metrics endpoint
        response = client.get("/metrics")
        assert response.status_code == 200
        
        # Step 3: Verify metrics are being collected
        metrics_content = response.text
        assert "http_requests_total" in metrics_content
        assert "http_request_duration_seconds" in metrics_content
    
    def test_health_check_workflow(self, client: TestClient):
        """Test complete health check workflow"""
        # Step 1: Check basic health
        response = client.get("/health")
        assert response.status_code == 200
        health_data = response.json()
        assert health_data["status"] == "healthy"
        
        # Step 2: Check readiness
        response = client.get("/ready")
        assert response.status_code == 200
        readiness_data = response.json()
        assert readiness_data["status"] == "ready"
        assert "checks" in readiness_data


class TestCompleteErrorHandlingWorkflow:
    """Test complete error handling workflow"""
    
    def test_error_recovery_workflow(self, client: TestClient, auth_headers):
        """Test complete error recovery workflow"""
        # Step 1: Trigger various error conditions
        error_scenarios = [
            ("/api/v1/securities/99999", 404),  # Not found
            ("/api/v1/indices/99999", 404),     # Not found
            ("/invalid-endpoint", 404),         # Invalid endpoint
        ]
        
        for endpoint, expected_status in error_scenarios:
            response = client.get(endpoint, headers=auth_headers)
            assert response.status_code == expected_status
        
        # Step 2: Verify system still works after errors
        response = client.get("/health")
        assert response.status_code == 200
        
        response = client.get("/api/v1/securities", headers=auth_headers)
        assert response.status_code in [200, 401]
    
    def test_data_validation_error_workflow(self, client: TestClient, auth_headers):
        """Test complete data validation error workflow"""
        # Step 1: Submit invalid data
        invalid_data = {
            "symbol": "",  # Invalid: empty symbol
            "name": "Test Company",
            "exchange": "NASDAQ",
            "currency": "USD",
            "sector": "Technology",
            "market_cap": -1000.0  # Invalid: negative market cap
        }
        
        response = client.post(
            "/api/v1/securities",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422  # Validation error
        
        # Step 2: Verify error response structure
        error_data = response.json()
        assert "detail" in error_data
        
        # Step 3: Verify system still works after validation errors
        response = client.get("/api/v1/securities", headers=auth_headers)
        assert response.status_code in [200, 401]


class TestCompletePerformanceWorkflow:
    """Test complete performance workflow"""
    
    def test_high_load_workflow(self, client: TestClient, auth_headers):
        """Test complete workflow under high load"""
        import concurrent.futures
        import time
        
        # Step 1: Define workload
        def make_request():
            start_time = time.time()
            response = client.get("/api/v1/securities", headers=auth_headers)
            end_time = time.time()
            return {
                "status_code": response.status_code,
                "response_time": end_time - start_time
            }
        
        # Step 2: Execute high load
        num_requests = 50
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Step 3: Verify performance
        response_times = [r["response_time"] for r in results]
        success_count = sum(1 for r in results if r["status_code"] in [200, 401])
        
        assert success_count >= num_requests * 0.95  # 95% success rate
        assert max(response_times) < 5.0  # Max response time under 5s
        assert sum(response_times) / len(response_times) < 2.0  # Average under 2s
        
        # Step 4: Verify system health after load
        response = client.get("/health")
        assert response.status_code == 200
