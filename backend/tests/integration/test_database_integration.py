"""
Integration tests for database operations
"""
import pytest
from sqlalchemy.orm import Session
from datetime import datetime, date

from app.db.models import User, Security, IndexDefinition, PriceData, IndexValue, IndexConstituent
from app.db.schemas import SecurityCreate, IndexDefinitionCreate, PriceDataCreate
from app.core.security import get_password_hash


class TestUserDatabaseOperations:
    """Test user database operations"""
    
    def test_create_user(self, db_session: Session):
        """Test creating a user in the database"""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "hashed_password": get_password_hash("testpassword"),
            "is_active": True
        }
        
        user = User(**user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.id is not None
        assert user.email == user_data["email"]
        assert user.username == user_data["username"]
        assert user.is_active is True
        assert user.created_at is not None
    
    def test_get_user_by_email(self, db_session: Session, test_user):
        """Test retrieving user by email"""
        user = db_session.query(User).filter(User.email == test_user.email).first()
        
        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email
    
    def test_get_user_by_username(self, db_session: Session, test_user):
        """Test retrieving user by username"""
        user = db_session.query(User).filter(User.username == test_user.username).first()
        
        assert user is not None
        assert user.id == test_user.id
        assert user.username == test_user.username
    
    def test_update_user(self, db_session: Session, test_user):
        """Test updating user information"""
        test_user.full_name = "Updated Name"
        test_user.is_active = False
        
        db_session.commit()
        db_session.refresh(test_user)
        
        assert test_user.full_name == "Updated Name"
        assert test_user.is_active is False
    
    def test_delete_user(self, db_session: Session):
        """Test deleting a user"""
        user = User(
            email="delete@example.com",
            username="deleteuser",
            full_name="Delete User",
            hashed_password=get_password_hash("password"),
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        user_id = user.id
        
        db_session.delete(user)
        db_session.commit()
        
        deleted_user = db_session.query(User).filter(User.id == user_id).first()
        assert deleted_user is None


class TestSecurityDatabaseOperations:
    """Test security database operations"""
    
    def test_create_security(self, db_session: Session):
        """Test creating a security in the database"""
        security_data = {
            "symbol": "TSLA",
            "name": "Tesla Inc.",
            "exchange": "NASDAQ",
            "currency": "USD",
            "sector": "Automotive",
            "industry": "Electric Vehicles",
            "country": "USA",
            "market_cap": 800000000000.0,
            "is_active": True
        }
        
        security = Security(**security_data)
        db_session.add(security)
        db_session.commit()
        db_session.refresh(security)
        
        assert security.id is not None
        assert security.symbol == security_data["symbol"]
        assert security.name == security_data["name"]
        assert security.market_cap == security_data["market_cap"]
    
    def test_get_security_by_symbol(self, db_session: Session, test_security):
        """Test retrieving security by symbol"""
        security = db_session.query(Security).filter(Security.symbol == test_security.symbol).first()
        
        assert security is not None
        assert security.id == test_security.id
        assert security.symbol == test_security.symbol
    
    def test_get_securities_by_sector(self, db_session: Session, test_security):
        """Test retrieving securities by sector"""
        securities = db_session.query(Security).filter(Security.sector == test_security.sector).all()
        
        assert len(securities) >= 1
        for security in securities:
            assert security.sector == test_security.sector
    
    def test_get_securities_by_country(self, db_session: Session, test_security):
        """Test retrieving securities by country"""
        securities = db_session.query(Security).filter(Security.country == test_security.country).all()
        
        assert len(securities) >= 1
        for security in securities:
            assert security.country == test_security.country
    
    def test_update_security(self, db_session: Session, test_security):
        """Test updating security information"""
        test_security.name = "Updated Company Name"
        test_security.market_cap = 3500000000000.0
        
        db_session.commit()
        db_session.refresh(test_security)
        
        assert test_security.name == "Updated Company Name"
        assert test_security.market_cap == 3500000000000.0
    
    def test_deactivate_security(self, db_session: Session, test_security):
        """Test deactivating a security"""
        test_security.is_active = False
        
        db_session.commit()
        db_session.refresh(test_security)
        
        assert test_security.is_active is False


class TestPriceDataDatabaseOperations:
    """Test price data database operations"""
    
    def test_create_price_data(self, db_session: Session, test_security):
        """Test creating price data in the database"""
        price_data = {
            "security_id": test_security.id,
            "date": date(2024, 1, 15),
            "open_price": 155.0,
            "high_price": 160.0,
            "low_price": 150.0,
            "close_price": 158.0,
            "volume": 2000000,
            "adjusted_close": 158.0,
            "dividend": 0.0,
            "split_ratio": 1.0
        }
        
        price = PriceData(**price_data)
        db_session.add(price)
        db_session.commit()
        db_session.refresh(price)
        
        assert price.id is not None
        assert price.security_id == test_security.id
        assert price.date == price_data["date"]
        assert price.close_price == price_data["close_price"]
    
    def test_get_price_data_by_security(self, db_session: Session, test_security, test_price_data):
        """Test retrieving price data by security"""
        prices = db_session.query(PriceData).filter(PriceData.security_id == test_security.id).all()
        
        assert len(prices) >= 1
        for price in prices:
            assert price.security_id == test_security.id
    
    def test_get_price_data_by_date_range(self, db_session: Session, test_security):
        """Test retrieving price data by date range"""
        # Create multiple price records
        for i in range(5):
            price = PriceData(
                security_id=test_security.id,
                date=date(2024, 1, i + 1),
                open_price=150.0 + i,
                high_price=155.0 + i,
                low_price=145.0 + i,
                close_price=152.0 + i,
                volume=1000000 + i * 100000,
                adjusted_close=152.0 + i,
                dividend=0.0,
                split_ratio=1.0
            )
            db_session.add(price)
        
        db_session.commit()
        
        # Query by date range
        start_date = date(2024, 1, 2)
        end_date = date(2024, 1, 4)
        
        prices = db_session.query(PriceData).filter(
            PriceData.security_id == test_security.id,
            PriceData.date >= start_date,
            PriceData.date <= end_date
        ).all()
        
        assert len(prices) == 3
        for price in prices:
            assert start_date <= price.date <= end_date
    
    def test_get_latest_price(self, db_session: Session, test_security):
        """Test getting the latest price for a security"""
        # Create price records with different dates
        dates = [date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3)]
        for i, date_val in enumerate(dates):
            price = PriceData(
                security_id=test_security.id,
                date=date_val,
                open_price=150.0 + i,
                high_price=155.0 + i,
                low_price=145.0 + i,
                close_price=152.0 + i,
                volume=1000000,
                adjusted_close=152.0 + i,
                dividend=0.0,
                split_ratio=1.0
            )
            db_session.add(price)
        
        db_session.commit()
        
        # Get latest price
        latest_price = db_session.query(PriceData).filter(
            PriceData.security_id == test_security.id
        ).order_by(PriceData.date.desc()).first()
        
        assert latest_price is not None
        assert latest_price.date == date(2024, 1, 3)
        assert latest_price.close_price == 154.0


class TestIndexDefinitionDatabaseOperations:
    """Test index definition database operations"""
    
    def test_create_index_definition(self, db_session: Session, test_user):
        """Test creating an index definition in the database"""
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
            "is_active": True,
            "created_by": test_user.id
        }
        
        index_def = IndexDefinition(**index_data)
        db_session.add(index_def)
        db_session.commit()
        db_session.refresh(index_def)
        
        assert index_def.id is not None
        assert index_def.name == index_data["name"]
        assert index_def.weighting_method == index_data["weighting_method"]
        assert index_def.created_by == test_user.id
    
    def test_get_index_by_name(self, db_session: Session, test_index_definition):
        """Test retrieving index by name"""
        index = db_session.query(IndexDefinition).filter(
            IndexDefinition.name == test_index_definition.name
        ).first()
        
        assert index is not None
        assert index.id == test_index_definition.id
        assert index.name == test_index_definition.name
    
    def test_get_indices_by_weighting_method(self, db_session: Session, test_index_definition):
        """Test retrieving indices by weighting method"""
        indices = db_session.query(IndexDefinition).filter(
            IndexDefinition.weighting_method == test_index_definition.weighting_method
        ).all()
        
        assert len(indices) >= 1
        for index in indices:
            assert index.weighting_method == test_index_definition.weighting_method
    
    def test_update_index_definition(self, db_session: Session, test_index_definition):
        """Test updating index definition"""
        test_index_definition.description = "Updated description"
        test_index_definition.max_constituents = 50
        
        db_session.commit()
        db_session.refresh(test_index_definition)
        
        assert test_index_definition.description == "Updated description"
        assert test_index_definition.max_constituents == 50


class TestIndexValueDatabaseOperations:
    """Test index value database operations"""
    
    def test_create_index_value(self, db_session: Session, test_index_definition):
        """Test creating index value in the database"""
        index_value_data = {
            "index_definition_id": test_index_definition.id,
            "date": date(2024, 1, 1),
            "index_value": 1000.0,
            "total_return": 0.0,
            "price_return": 0.0,
            "dividend_yield": 0.02,
            "volatility": 0.15,
            "sharpe_ratio": 1.2
        }
        
        index_value = IndexValue(**index_value_data)
        db_session.add(index_value)
        db_session.commit()
        db_session.refresh(index_value)
        
        assert index_value.id is not None
        assert index_value.index_definition_id == test_index_definition.id
        assert index_value.index_value == index_value_data["index_value"]
    
    def test_get_index_values_by_index(self, db_session: Session, test_index_definition):
        """Test retrieving index values by index definition"""
        # Create multiple index values
        for i in range(5):
            index_value = IndexValue(
                index_definition_id=test_index_definition.id,
                date=date(2024, 1, i + 1),
                index_value=1000.0 + i * 10,
                total_return=i * 0.01,
                price_return=i * 0.008,
                dividend_yield=0.02,
                volatility=0.15,
                sharpe_ratio=1.2
            )
            db_session.add(index_value)
        
        db_session.commit()
        
        # Query index values
        index_values = db_session.query(IndexValue).filter(
            IndexValue.index_definition_id == test_index_definition.id
        ).order_by(IndexValue.date).all()
        
        assert len(index_values) == 5
        for i, value in enumerate(index_values):
            assert value.index_definition_id == test_index_definition.id
            assert value.index_value == 1000.0 + i * 10
    
    def test_get_latest_index_value(self, db_session: Session, test_index_definition):
        """Test getting the latest index value"""
        # Create index values with different dates
        dates = [date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3)]
        for i, date_val in enumerate(dates):
            index_value = IndexValue(
                index_definition_id=test_index_definition.id,
                date=date_val,
                index_value=1000.0 + i * 10,
                total_return=i * 0.01,
                price_return=i * 0.008,
                dividend_yield=0.02,
                volatility=0.15,
                sharpe_ratio=1.2
            )
            db_session.add(index_value)
        
        db_session.commit()
        
        # Get latest index value
        latest_value = db_session.query(IndexValue).filter(
            IndexValue.index_definition_id == test_index_definition.id
        ).order_by(IndexValue.date.desc()).first()
        
        assert latest_value is not None
        assert latest_value.date == date(2024, 1, 3)
        assert latest_value.index_value == 1020.0


class TestIndexConstituentDatabaseOperations:
    """Test index constituent database operations"""
    
    def test_create_index_constituent(self, db_session: Session, test_index_definition, test_security):
        """Test creating index constituent in the database"""
        constituent_data = {
            "index_definition_id": test_index_definition.id,
            "security_id": test_security.id,
            "date": date(2024, 1, 1),
            "weight": 0.1,
            "shares": 1000000,
            "market_cap": 150000000000,
            "is_new_addition": True,
            "is_removal": False
        }
        
        constituent = IndexConstituent(**constituent_data)
        db_session.add(constituent)
        db_session.commit()
        db_session.refresh(constituent)
        
        assert constituent.id is not None
        assert constituent.index_definition_id == test_index_definition.id
        assert constituent.security_id == test_security.id
        assert constituent.weight == constituent_data["weight"]
    
    def test_get_constituents_by_index(self, db_session: Session, test_index_definition, test_security):
        """Test retrieving constituents by index definition"""
        # Create multiple constituents
        securities = []
        for i in range(3):
            security = Security(
                symbol=f"TEST{i}",
                name=f"Test Company {i}",
                exchange="NASDAQ",
                currency="USD",
                sector="Technology",
                industry="Software",
                country="USA",
                market_cap=1000000000.0 + i * 1000000000.0,
                is_active=True
            )
            db_session.add(security)
            securities.append(security)
        
        db_session.commit()
        
        # Create constituents
        for i, security in enumerate(securities):
            constituent = IndexConstituent(
                index_definition_id=test_index_definition.id,
                security_id=security.id,
                date=date(2024, 1, 1),
                weight=0.1 + i * 0.05,
                shares=1000000,
                market_cap=security.market_cap,
                is_new_addition=True,
                is_removal=False
            )
            db_session.add(constituent)
        
        db_session.commit()
        
        # Query constituents
        constituents = db_session.query(IndexConstituent).filter(
            IndexConstituent.index_definition_id == test_index_definition.id
        ).all()
        
        assert len(constituents) == 3
        for constituent in constituents:
            assert constituent.index_definition_id == test_index_definition.id
    
    def test_get_constituents_by_date(self, db_session: Session, test_index_definition, test_security):
        """Test retrieving constituents by date"""
        # Create constituents for different dates
        dates = [date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3)]
        for i, date_val in enumerate(dates):
            constituent = IndexConstituent(
                index_definition_id=test_index_definition.id,
                security_id=test_security.id,
                date=date_val,
                weight=0.1 + i * 0.01,
                shares=1000000,
                market_cap=150000000000,
                is_new_addition=i == 0,
                is_removal=False
            )
            db_session.add(constituent)
        
        db_session.commit()
        
        # Query constituents for specific date
        target_date = date(2024, 1, 2)
        constituents = db_session.query(IndexConstituent).filter(
            IndexConstituent.index_definition_id == test_index_definition.id,
            IndexConstituent.date == target_date
        ).all()
        
        assert len(constituents) == 1
        assert constituents[0].date == target_date
        assert constituents[0].weight == 0.11


class TestDatabaseRelationships:
    """Test database relationships and foreign keys"""
    
    def test_security_price_relationship(self, db_session: Session, test_security):
        """Test relationship between security and price data"""
        # Create price data
        price = PriceData(
            security_id=test_security.id,
            date=date(2024, 1, 1),
            open_price=150.0,
            high_price=155.0,
            low_price=145.0,
            close_price=152.0,
            volume=1000000,
            adjusted_close=152.0,
            dividend=0.0,
            split_ratio=1.0
        )
        db_session.add(price)
        db_session.commit()
        
        # Test relationship
        security = db_session.query(Security).filter(Security.id == test_security.id).first()
        assert security is not None
        
        # Access price data through relationship
        prices = db_session.query(PriceData).filter(PriceData.security_id == security.id).all()
        assert len(prices) >= 1
        assert prices[0].security_id == security.id
    
    def test_index_definition_constituent_relationship(self, db_session: Session, test_index_definition, test_security):
        """Test relationship between index definition and constituents"""
        # Create constituent
        constituent = IndexConstituent(
            index_definition_id=test_index_definition.id,
            security_id=test_security.id,
            date=date(2024, 1, 1),
            weight=0.1,
            shares=1000000,
            market_cap=150000000000,
            is_new_addition=True,
            is_removal=False
        )
        db_session.add(constituent)
        db_session.commit()
        
        # Test relationship
        index_def = db_session.query(IndexDefinition).filter(
            IndexDefinition.id == test_index_definition.id
        ).first()
        assert index_def is not None
        
        # Access constituents through relationship
        constituents = db_session.query(IndexConstituent).filter(
            IndexConstituent.index_definition_id == index_def.id
        ).all()
        assert len(constituents) >= 1
        assert constituents[0].index_definition_id == index_def.id
    
    def test_user_index_definition_relationship(self, db_session: Session, test_user):
        """Test relationship between user and index definitions"""
        # Create index definition
        index_def = IndexDefinition(
            name="User Test Index",
            description="Test index created by user",
            weighting_method="equal_weight",
            rebalance_frequency="monthly",
            max_constituents=10,
            min_market_cap=1000000000.0,
            max_market_cap=1000000000000.0,
            sectors=["Technology"],
            countries=["USA"],
            esg_criteria={"min_esg_score": 7.0},
            is_active=True,
            created_by=test_user.id
        )
        db_session.add(index_def)
        db_session.commit()
        
        # Test relationship
        user = db_session.query(User).filter(User.id == test_user.id).first()
        assert user is not None
        
        # Access index definitions through relationship
        index_defs = db_session.query(IndexDefinition).filter(
            IndexDefinition.created_by == user.id
        ).all()
        assert len(index_defs) >= 1
        assert index_defs[0].created_by == user.id


class TestDatabaseConstraints:
    """Test database constraints and validations"""
    
    def test_unique_symbol_constraint(self, db_session: Session):
        """Test unique symbol constraint"""
        # Create first security
        security1 = Security(
            symbol="UNIQUE",
            name="First Company",
            exchange="NASDAQ",
            currency="USD",
            sector="Technology",
            industry="Software",
            country="USA",
            market_cap=1000000000.0,
            is_active=True
        )
        db_session.add(security1)
        db_session.commit()
        
        # Try to create second security with same symbol
        security2 = Security(
            symbol="UNIQUE",  # Same symbol
            name="Second Company",
            exchange="NASDAQ",
            currency="USD",
            sector="Technology",
            industry="Software",
            country="USA",
            market_cap=2000000000.0,
            is_active=True
        )
        db_session.add(security2)
        
        # Should raise integrity error
        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()
    
    def test_foreign_key_constraints(self, db_session: Session):
        """Test foreign key constraints"""
        # Try to create price data with non-existent security
        price = PriceData(
            security_id=99999,  # Non-existent security
            date=date(2024, 1, 1),
            open_price=150.0,
            high_price=155.0,
            low_price=145.0,
            close_price=152.0,
            volume=1000000,
            adjusted_close=152.0,
            dividend=0.0,
            split_ratio=1.0
        )
        db_session.add(price)
        
        # Should raise integrity error
        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()
    
    def test_not_null_constraints(self, db_session: Session):
        """Test not null constraints"""
        # Try to create security without required fields
        security = Security(
            symbol=None,  # Required field
            name="Test Company",
            exchange="NASDAQ",
            currency="USD",
            sector="Technology",
            industry="Software",
            country="USA",
            market_cap=1000000000.0,
            is_active=True
        )
        db_session.add(security)
        
        # Should raise integrity error
        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()
