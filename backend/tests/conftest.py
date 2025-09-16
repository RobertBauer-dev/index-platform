"""
Pytest configuration and fixtures for Index Platform tests
"""
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db, Base
from app.core.config import settings
from app.db.models import User, Security, IndexDefinition, PriceData
from app.core.security import get_password_hash


# Test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session) -> Generator[TestClient, None, None]:
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password=get_password_hash("testpassword"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_admin_user(db_session):
    """Create a test admin user."""
    user = User(
        email="admin@example.com",
        username="admin",
        full_name="Admin User",
        hashed_password=get_password_hash("adminpassword"),
        is_active=True,
        is_superuser=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_security(db_session):
    """Create a test security."""
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
    db_session.add(security)
    db_session.commit()
    db_session.refresh(security)
    return security


@pytest.fixture
def test_index_definition(db_session, test_user):
    """Create a test index definition."""
    index_def = IndexDefinition(
        name="Test Index",
        description="A test index",
        weighting_method="equal_weight",
        rebalance_frequency="monthly",
        max_constituents=50,
        min_market_cap=1000000000.0,
        max_market_cap=1000000000000.0,
        sectors=["Technology", "Healthcare"],
        countries=["USA", "Germany"],
        esg_criteria={"min_esg_score": 7.0},
        is_active=True,
        created_by=test_user.id
    )
    db_session.add(index_def)
    db_session.commit()
    db_session.refresh(index_def)
    return index_def


@pytest.fixture
def test_price_data(db_session, test_security):
    """Create test price data."""
    price_data = PriceData(
        security_id=test_security.id,
        date="2024-01-01",
        open_price=150.0,
        high_price=155.0,
        low_price=148.0,
        close_price=152.0,
        volume=1000000,
        adjusted_close=152.0,
        dividend=0.0,
        split_ratio=1.0
    )
    db_session.add(price_data)
    db_session.commit()
    db_session.refresh(price_data)
    return price_data


@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for test user."""
    response = client.post(
        "/api/v1/auth/token",
        data={"username": test_user.username, "password": "testpassword"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(client, test_admin_user):
    """Get authentication headers for admin user."""
    response = client.post(
        "/api/v1/auth/token",
        data={"username": test_admin_user.username, "password": "adminpassword"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_securities_data():
    """Sample securities data for testing."""
    return [
        {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "exchange": "NASDAQ",
            "currency": "USD",
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "country": "USA",
            "market_cap": 3000000000000.0
        },
        {
            "symbol": "MSFT",
            "name": "Microsoft Corporation",
            "exchange": "NASDAQ",
            "currency": "USD",
            "sector": "Technology",
            "industry": "Software",
            "country": "USA",
            "market_cap": 2800000000000.0
        },
        {
            "symbol": "GOOGL",
            "name": "Alphabet Inc.",
            "exchange": "NASDAQ",
            "currency": "USD",
            "sector": "Technology",
            "industry": "Internet",
            "country": "USA",
            "market_cap": 1800000000000.0
        }
    ]


@pytest.fixture
def sample_price_data():
    """Sample price data for testing."""
    return [
        {
            "symbol": "AAPL",
            "date": "2024-01-01",
            "open_price": 150.0,
            "high_price": 155.0,
            "low_price": 148.0,
            "close_price": 152.0,
            "volume": 1000000,
            "adjusted_close": 152.0,
            "dividend": 0.0,
            "split_ratio": 1.0
        },
        {
            "symbol": "AAPL",
            "date": "2024-01-02",
            "open_price": 152.0,
            "high_price": 158.0,
            "low_price": 151.0,
            "close_price": 156.0,
            "volume": 1200000,
            "adjusted_close": 156.0,
            "dividend": 0.0,
            "split_ratio": 1.0
        }
    ]


@pytest.fixture
def sample_index_definition_data():
    """Sample index definition data for testing."""
    return {
        "name": "Technology Leaders Index",
        "description": "An index of leading technology companies",
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


# Performance test fixtures
@pytest.fixture
def large_dataset_securities():
    """Large dataset of securities for performance testing."""
    securities = []
    for i in range(1000):
        securities.append({
            "symbol": f"STOCK{i:04d}",
            "name": f"Test Company {i}",
            "exchange": "TEST",
            "currency": "USD",
            "sector": "Technology" if i % 2 == 0 else "Healthcare",
            "industry": "Software" if i % 2 == 0 else "Pharmaceuticals",
            "country": "USA" if i % 3 == 0 else "Germany" if i % 3 == 1 else "Japan",
            "market_cap": 1000000000.0 + (i * 1000000.0)
        })
    return securities


@pytest.fixture
def large_dataset_prices():
    """Large dataset of price data for performance testing."""
    prices = []
    for security_id in range(1, 101):  # 100 securities
        for day in range(365):  # 1 year of data
            prices.append({
                "security_id": security_id,
                "date": f"2024-01-{day+1:02d}",
                "open_price": 100.0 + (day * 0.1),
                "high_price": 105.0 + (day * 0.1),
                "low_price": 95.0 + (day * 0.1),
                "close_price": 102.0 + (day * 0.1),
                "volume": 1000000 + (day * 1000),
                "adjusted_close": 102.0 + (day * 0.1),
                "dividend": 0.0,
                "split_ratio": 1.0
            })
    return prices
