"""
Locust load testing configuration for Index Platform
"""
from locust import HttpUser, task, between
import random
import json


class IndexPlatformUser(HttpUser):
    """Simulate user behavior on Index Platform"""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Called when a user starts"""
        # Login and get authentication token
        self.login()
    
    def login(self):
        """Login and store authentication token"""
        response = self.client.post(
            "/api/v1/auth/token",
            data={
                "username": "admin",
                "password": "admin123"
            }
        )
        
        if response.status_code == 200:
            token_data = response.json()
            self.token = token_data["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}
    
    @task(10)
    def get_securities(self):
        """Get list of securities (most common operation)"""
        self.client.get("/api/v1/securities", headers=self.headers)
    
    @task(8)
    def get_indices(self):
        """Get list of indices"""
        self.client.get("/api/v1/indices", headers=self.headers)
    
    @task(5)
    def get_security_details(self):
        """Get specific security details"""
        # Use a random security ID (assuming IDs 1-100 exist)
        security_id = random.randint(1, 100)
        self.client.get(f"/api/v1/securities/{security_id}", headers=self.headers)
    
    @task(5)
    def get_index_details(self):
        """Get specific index details"""
        # Use a random index ID (assuming IDs 1-50 exist)
        index_id = random.randint(1, 50)
        self.client.get(f"/api/v1/indices/{index_id}", headers=self.headers)
    
    @task(3)
    def get_price_data(self):
        """Get price data for a security"""
        security_id = random.randint(1, 100)
        params = {
            "start_date": "2024-01-01",
            "end_date": "2024-01-31"
        }
        self.client.get(
            f"/api/v1/securities/{security_id}/prices",
            params=params,
            headers=self.headers
        )
    
    @task(2)
    def get_index_values(self):
        """Get index values"""
        index_id = random.randint(1, 50)
        self.client.get(f"/api/v1/indices/{index_id}/values", headers=self.headers)
    
    @task(1)
    def calculate_index(self):
        """Calculate index (expensive operation)"""
        index_id = random.randint(1, 50)
        self.client.post(f"/api/v1/indices/{index_id}/calculate", headers=self.headers)
    
    @task(1)
    def run_backtest(self):
        """Run index backtest (very expensive operation)"""
        index_id = random.randint(1, 50)
        backtest_data = {
            "start_date": "2024-01-01",
            "end_date": "2024-01-31"
        }
        self.client.post(
            f"/api/v1/indices/{index_id}/backtest",
            json=backtest_data,
            headers=self.headers
        )
    
    @task(3)
    def create_custom_index(self):
        """Create a custom index"""
        index_data = {
            "name": f"Load Test Index {random.randint(1000, 9999)}",
            "description": "Index created during load testing",
            "weighting_method": random.choice(["equal_weight", "market_cap_weight"]),
            "rebalance_frequency": "monthly",
            "max_constituents": random.randint(10, 50),
            "min_market_cap": 1000000000.0,
            "max_market_cap": 1000000000000.0,
            "sectors": ["Technology"],
            "countries": ["USA"],
            "esg_criteria": {"min_esg_score": 6.0},
            "is_active": True
        }
        self.client.post("/api/v1/indices", json=index_data, headers=self.headers)
    
    @task(2)
    def get_health_check(self):
        """Get health check (no authentication required)"""
        self.client.get("/health")
    
    @task(1)
    def get_metrics(self):
        """Get metrics (no authentication required)"""
        self.client.get("/metrics")


class AnonymousUser(HttpUser):
    """Simulate anonymous user behavior"""
    
    wait_time = between(2, 5)
    
    @task(5)
    def get_health_check(self):
        """Get health check"""
        self.client.get("/health")
    
    @task(3)
    def get_metrics(self):
        """Get metrics"""
        self.client.get("/metrics")
    
    @task(1)
    def try_unauthorized_access(self):
        """Try to access protected endpoints without authentication"""
        self.client.get("/api/v1/securities")
        self.client.get("/api/v1/indices")


class DataIngestionUser(HttpUser):
    """Simulate data ingestion operations"""
    
    wait_time = between(5, 10)  # Longer wait time for data operations
    
    def on_start(self):
        """Login as admin for data operations"""
        self.login()
    
    def login(self):
        """Login and store authentication token"""
        response = self.client.post(
            "/api/v1/auth/token",
            data={
                "username": "admin",
                "password": "admin123"
            }
        )
        
        if response.status_code == 200:
            token_data = response.json()
            self.token = token_data["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}
    
    @task(1)
    def ingest_securities_csv(self):
        """Simulate CSV securities ingestion"""
        # Create sample CSV content
        csv_content = """symbol,name,exchange,currency,sector,industry,country,market_cap
TEST1,Test Company 1,NASDAQ,USD,Technology,Software,USA,1000000000
TEST2,Test Company 2,NASDAQ,USD,Technology,Hardware,USA,2000000000"""
        
        files = {"file": ("securities.csv", csv_content, "text/csv")}
        self.client.post(
            "/api/v1/ingestion/csv/securities",
            files=files,
            headers=self.headers
        )
    
    @task(1)
    def ingest_prices_csv(self):
        """Simulate CSV price data ingestion"""
        # Create sample price CSV content
        csv_content = """symbol,date,open_price,high_price,low_price,close_price,volume,adjusted_close,dividend,split_ratio
TEST1,2024-01-01,100.0,105.0,95.0,102.0,1000000,102.0,0.0,1.0
TEST1,2024-01-02,102.0,108.0,100.0,106.0,1200000,106.0,0.0,1.0"""
        
        files = {"file": ("prices.csv", csv_content, "text/csv")}
        self.client.post(
            "/api/v1/ingestion/csv/prices",
            files=files,
            headers=self.headers
        )
    
    @task(1)
    def ingest_alpha_vantage_data(self):
        """Simulate Alpha Vantage data ingestion"""
        ingestion_data = {
            "symbol": "AAPL",
            "api_key": "test_key"
        }
        self.client.post(
            "/api/v1/ingestion/api/alpha-vantage",
            json=ingestion_data,
            headers=self.headers
        )


class GraphQLUser(HttpUser):
    """Simulate GraphQL API usage"""
    
    wait_time = between(1, 2)
    
    def on_start(self):
        """Login and get authentication token"""
        self.login()
    
    def login(self):
        """Login and store authentication token"""
        response = self.client.post(
            "/api/v1/auth/token",
            data={
                "username": "admin",
                "password": "admin123"
            }
        )
        
        if response.status_code == 200:
            token_data = response.json()
            self.token = token_data["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}
    
    @task(5)
    def query_securities(self):
        """Query securities via GraphQL"""
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
        
        self.client.post(
            "/graphql",
            json={"query": query},
            headers=self.headers
        )
    
    @task(3)
    def query_indices(self):
        """Query indices via GraphQL"""
        query = """
        query {
            indices {
                edges {
                    node {
                        id
                        name
                        description
                        weightingMethod
                    }
                }
            }
        }
        """
        
        self.client.post(
            "/graphql",
            json={"query": query},
            headers=self.headers
        )
    
    @task(2)
    def query_index_values(self):
        """Query index values via GraphQL"""
        index_id = random.randint(1, 50)
        query = f"""
        query {{
            index(id: {index_id}) {{
                name
                indexValues {{
                    date
                    indexValue
                    totalReturn
                }}
            }}
        }}
        """
        
        self.client.post(
            "/graphql",
            json={"query": query},
            headers=self.headers
        )
    
    @task(1)
    def create_index_mutation(self):
        """Create index via GraphQL mutation"""
        mutation = """
        mutation {
            createIndexDefinition(input: {
                name: "GraphQL Load Test Index"
                description: "Index created during GraphQL load testing"
                weightingMethod: equal_weight
                rebalanceFrequency: monthly
                maxConstituents: 20
                minMarketCap: 1000000000.0
                maxMarketCap: 1000000000000.0
                sectors: ["Technology"]
                countries: ["USA"]
                esgCriteria: {minEsgScore: 6.0}
                isActive: true
            }) {
                indexDefinition {
                    id
                    name
                    weightingMethod
                }
            }
        }
        """
        
        self.client.post(
            "/graphql",
            json={"query": mutation},
            headers=self.headers
        )
