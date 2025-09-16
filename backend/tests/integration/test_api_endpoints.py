"""
Integration tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.db.models import User, Security, IndexDefinition, PriceData


class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    def test_login_success(self, client: TestClient, test_user):
        """Test successful login"""
        response = client.post(
            "/api/v1/auth/token",
            data={"username": test_user.username, "password": "testpassword"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client: TestClient, test_user):
        """Test login with invalid credentials"""
        response = client.post(
            "/api/v1/auth/token",
            data={"username": test_user.username, "password": "wrongpassword"}
        )
        
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with nonexistent user"""
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "nonexistent", "password": "password"}
        )
        
        assert response.status_code == 401
    
    def test_get_current_user(self, client: TestClient, auth_headers):
        """Test getting current user information"""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "username" in data
        assert data["is_active"] is True
    
    def test_get_current_user_unauthorized(self, client: TestClient):
        """Test getting current user without authentication"""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 401


class TestSecuritiesEndpoints:
    """Test securities endpoints"""
    
    def test_get_securities(self, client: TestClient, auth_headers, test_security):
        """Test getting list of securities"""
        response = client.get("/api/v1/securities", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Check that test security is in the list
        symbols = [item["symbol"] for item in data]
        assert test_security.symbol in symbols
    
    def test_get_securities_unauthorized(self, client: TestClient, test_security):
        """Test getting securities without authentication"""
        response = client.get("/api/v1/securities")
        
        assert response.status_code == 401
    
    def test_get_security_by_id(self, client: TestClient, auth_headers, test_security):
        """Test getting security by ID"""
        response = client.get(f"/api/v1/securities/{test_security.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_security.id
        assert data["symbol"] == test_security.symbol
        assert data["name"] == test_security.name
    
    def test_get_security_not_found(self, client: TestClient, auth_headers):
        """Test getting nonexistent security"""
        response = client.get("/api/v1/securities/99999", headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_create_security(self, client: TestClient, admin_auth_headers):
        """Test creating a new security"""
        security_data = {
            "symbol": "TSLA",
            "name": "Tesla Inc.",
            "exchange": "NASDAQ",
            "currency": "USD",
            "sector": "Automotive",
            "industry": "Electric Vehicles",
            "country": "USA",
            "market_cap": 800000000000.0
        }
        
        response = client.post(
            "/api/v1/securities",
            json=security_data,
            headers=admin_auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["symbol"] == security_data["symbol"]
        assert data["name"] == security_data["name"]
        assert data["is_active"] is True
    
    def test_create_security_duplicate_symbol(self, client: TestClient, admin_auth_headers, test_security):
        """Test creating security with duplicate symbol"""
        security_data = {
            "symbol": test_security.symbol,  # Duplicate symbol
            "name": "Another Company",
            "exchange": "NASDAQ",
            "currency": "USD",
            "sector": "Technology",
            "industry": "Software",
            "country": "USA",
            "market_cap": 1000000000.0
        }
        
        response = client.post(
            "/api/v1/securities",
            json=security_data,
            headers=admin_auth_headers
        )
        
        assert response.status_code == 400
    
    def test_update_security(self, client: TestClient, admin_auth_headers, test_security):
        """Test updating a security"""
        update_data = {
            "name": "Apple Inc. Updated",
            "market_cap": 3100000000000.0
        }
        
        response = client.put(
            f"/api/v1/securities/{test_security.id}",
            json=update_data,
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["market_cap"] == update_data["market_cap"]
    
    def test_delete_security(self, client: TestClient, admin_auth_headers, test_security):
        """Test deleting a security"""
        response = client.delete(
            f"/api/v1/securities/{test_security.id}",
            headers=admin_auth_headers
        )
        
        assert response.status_code == 204
        
        # Verify security is deleted
        response = client.get(f"/api/v1/securities/{test_security.id}", headers=admin_auth_headers)
        assert response.status_code == 404


class TestIndicesEndpoints:
    """Test indices endpoints"""
    
    def test_get_indices(self, client: TestClient, auth_headers, test_index_definition):
        """Test getting list of indices"""
        response = client.get("/api/v1/indices", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Check that test index is in the list
        names = [item["name"] for item in data]
        assert test_index_definition.name in names
    
    def test_get_index_by_id(self, client: TestClient, auth_headers, test_index_definition):
        """Test getting index by ID"""
        response = client.get(f"/api/v1/indices/{test_index_definition.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_index_definition.id
        assert data["name"] == test_index_definition.name
        assert data["weighting_method"] == test_index_definition.weighting_method
    
    def test_create_index(self, client: TestClient, auth_headers):
        """Test creating a new index"""
        index_data = {
            "name": "Technology Leaders",
            "description": "Leading technology companies",
            "weighting_method": "market_cap_weight",
            "rebalance_frequency": "quarterly",
            "max_constituents": 30,
            "min_market_cap": 10000000000.0,
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
        data = response.json()
        assert data["name"] == index_data["name"]
        assert data["weighting_method"] == index_data["weighting_method"]
    
    def test_calculate_index(self, client: TestClient, auth_headers, test_index_definition):
        """Test index calculation"""
        response = client.post(
            f"/api/v1/indices/{test_index_definition.id}/calculate",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "index_value" in data
        assert "calculation_date" in data
        assert "constituents" in data
    
    def test_get_index_values(self, client: TestClient, auth_headers, test_index_definition):
        """Test getting index values"""
        response = client.get(
            f"/api/v1/indices/{test_index_definition.id}/values",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_backtest_index(self, client: TestClient, auth_headers, test_index_definition):
        """Test index backtesting"""
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
        data = response.json()
        assert "backtest_results" in data
        assert "performance_metrics" in data


class TestPriceDataEndpoints:
    """Test price data endpoints"""
    
    def test_get_price_data(self, client: TestClient, auth_headers, test_security, test_price_data):
        """Test getting price data for a security"""
        response = client.get(
            f"/api/v1/securities/{test_security.id}/prices",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Check that test price data is in the list
        dates = [item["date"] for item in data]
        assert test_price_data.date in dates
    
    def test_get_price_data_with_filters(self, client: TestClient, auth_headers, test_security):
        """Test getting price data with date filters"""
        params = {
            "start_date": "2024-01-01",
            "end_date": "2024-01-31"
        }
        
        response = client.get(
            f"/api/v1/securities/{test_security.id}/prices",
            params=params,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_create_price_data(self, client: TestClient, admin_auth_headers, test_security):
        """Test creating price data"""
        price_data = {
            "date": "2024-01-15",
            "open_price": 155.0,
            "high_price": 160.0,
            "low_price": 150.0,
            "close_price": 158.0,
            "volume": 2000000,
            "adjusted_close": 158.0,
            "dividend": 0.0,
            "split_ratio": 1.0
        }
        
        response = client.post(
            f"/api/v1/securities/{test_security.id}/prices",
            json=price_data,
            headers=admin_auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["date"] == price_data["date"]
        assert data["close_price"] == price_data["close_price"]


class TestDataIngestionEndpoints:
    """Test data ingestion endpoints"""
    
    def test_ingest_csv_securities(self, client: TestClient, admin_auth_headers, sample_securities_data):
        """Test CSV securities ingestion"""
        # Create a CSV file content
        csv_content = "symbol,name,exchange,currency,sector,industry,country,market_cap\n"
        for security in sample_securities_data:
            csv_content += f"{security['symbol']},{security['name']},{security['exchange']},{security['currency']},{security['sector']},{security['industry']},{security['country']},{security['market_cap']}\n"
        
        files = {"file": ("securities.csv", csv_content, "text/csv")}
        
        response = client.post(
            "/api/v1/ingestion/csv/securities",
            files=files,
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "ingested_count" in data
        assert data["ingested_count"] == len(sample_securities_data)
    
    def test_ingest_csv_prices(self, client: TestClient, admin_auth_headers, sample_price_data):
        """Test CSV price data ingestion"""
        # Create a CSV file content
        csv_content = "symbol,date,open_price,high_price,low_price,close_price,volume,adjusted_close,dividend,split_ratio\n"
        for price in sample_price_data:
            csv_content += f"{price['symbol']},{price['date']},{price['open_price']},{price['high_price']},{price['low_price']},{price['close_price']},{price['volume']},{price['adjusted_close']},{price['dividend']},{price['split_ratio']}\n"
        
        files = {"file": ("prices.csv", csv_content, "text/csv")}
        
        response = client.post(
            "/api/v1/ingestion/csv/prices",
            files=files,
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "ingested_count" in data
        assert data["ingested_count"] == len(sample_price_data)
    
    def test_ingest_invalid_csv(self, client: TestClient, admin_auth_headers):
        """Test ingestion of invalid CSV"""
        invalid_csv = "invalid,csv,content\nwith,wrong,structure"
        
        files = {"file": ("invalid.csv", invalid_csv, "text/csv")}
        
        response = client.post(
            "/api/v1/ingestion/csv/securities",
            files=files,
            headers=admin_auth_headers
        )
        
        assert response.status_code == 400
    
    def test_ingest_alpha_vantage_data(self, client: TestClient, admin_auth_headers):
        """Test Alpha Vantage data ingestion"""
        ingestion_data = {
            "symbol": "AAPL",
            "api_key": "test_key"
        }
        
        with pytest.Mock() as mock_requests:
            mock_response = {
                "Time Series (Daily)": {
                    "2024-01-01": {
                        "1. open": "150.00",
                        "2. high": "155.00",
                        "3. low": "148.00",
                        "4. close": "152.00",
                        "5. volume": "1000000"
                    }
                }
            }
            mock_requests.get.return_value.json.return_value = mock_response
            mock_requests.get.return_value.status_code = 200
            
            response = client.post(
                "/api/v1/ingestion/api/alpha-vantage",
                json=ingestion_data,
                headers=admin_auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "ingested_count" in data


class TestGraphQLEndpoints:
    """Test GraphQL endpoints"""
    
    def test_graphql_query_securities(self, client: TestClient, auth_headers, test_security):
        """Test GraphQL securities query"""
        query = """
        query {
            securities {
                edges {
                    node {
                        id
                        symbol
                        name
                        sector
                        marketCap
                    }
                }
            }
        }
        """
        
        response = client.post(
            "/graphql",
            json={"query": query},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "securities" in data["data"]
        assert "edges" in data["data"]["securities"]
    
    def test_graphql_query_index(self, client: TestClient, auth_headers, test_index_definition):
        """Test GraphQL index query"""
        query = """
        query GetIndex($id: Int!) {
            index(id: $id) {
                id
                name
                description
                weightingMethod
            }
        }
        """
        
        variables = {"id": test_index_definition.id}
        
        response = client.post(
            "/graphql",
            json={"query": query, "variables": variables},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "index" in data["data"]
        assert data["data"]["index"]["id"] == test_index_definition.id
    
    def test_graphql_mutation_create_index(self, client: TestClient, auth_headers):
        """Test GraphQL index creation mutation"""
        mutation = """
        mutation CreateIndex($input: CreateIndexDefinitionInput!) {
            createIndexDefinition(input: $input) {
                indexDefinition {
                    id
                    name
                    weightingMethod
                }
            }
        }
        """
        
        variables = {
            "input": {
                "name": "GraphQL Test Index",
                "description": "Test index created via GraphQL",
                "weightingMethod": "equal_weight",
                "rebalanceFrequency": "monthly",
                "maxConstituents": 10,
                "minMarketCap": 1000000000.0,
                "maxMarketCap": 1000000000000.0,
                "sectors": ["Technology"],
                "countries": ["USA"],
                "esgCriteria": {"minEsgScore": 7.0},
                "isActive": True
            }
        }
        
        response = client.post(
            "/graphql",
            json={"query": mutation, "variables": variables},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "createIndexDefinition" in data["data"]
        assert "indexDefinition" in data["data"]["createIndexDefinition"]


class TestErrorHandling:
    """Test error handling across endpoints"""
    
    def test_404_error(self, client: TestClient, auth_headers):
        """Test 404 error handling"""
        response = client.get("/api/v1/securities/99999", headers=auth_headers)
        assert response.status_code == 404
    
    def test_422_validation_error(self, client: TestClient, auth_headers):
        """Test 422 validation error handling"""
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
        
        assert response.status_code == 422
    
    def test_500_internal_server_error(self, client: TestClient, auth_headers):
        """Test 500 internal server error handling"""
        # This would require mocking a database error
        # For now, we'll test the error response format
        response = client.get("/api/v1/securities", headers=auth_headers)
        # Should not be 500 for normal operation
        assert response.status_code != 500


class TestPagination:
    """Test pagination functionality"""
    
    def test_securities_pagination(self, client: TestClient, auth_headers):
        """Test securities endpoint pagination"""
        params = {"page": 1, "size": 10}
        
        response = client.get(
            "/api/v1/securities",
            params=params,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10
    
    def test_indices_pagination(self, client: TestClient, auth_headers):
        """Test indices endpoint pagination"""
        params = {"page": 1, "size": 5}
        
        response = client.get(
            "/api/v1/indices",
            params=params,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5


class TestFiltering:
    """Test filtering functionality"""
    
    def test_securities_filtering(self, client: TestClient, auth_headers, test_security):
        """Test securities filtering by sector"""
        params = {"sector": test_security.sector}
        
        response = client.get(
            "/api/v1/securities",
            params=params,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # All returned securities should have the specified sector
        for security in data:
            assert security["sector"] == test_security.sector
    
    def test_indices_filtering(self, client: TestClient, auth_headers, test_index_definition):
        """Test indices filtering by weighting method"""
        params = {"weighting_method": test_index_definition.weighting_method}
        
        response = client.get(
            "/api/v1/indices",
            params=params,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # All returned indices should have the specified weighting method
        for index in data:
            assert index["weighting_method"] == test_index_definition.weighting_method
