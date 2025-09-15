"""
GraphQL schema and resolvers
"""
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from graphene import relay
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.db import models


class SecurityType(SQLAlchemyObjectType):
    class Meta:
        model = models.Security
        interfaces = (relay.Node,)


class PriceDataType(SQLAlchemyObjectType):
    class Meta:
        model = models.PriceData
        interfaces = (relay.Node,)


class IndexDefinitionType(SQLAlchemyObjectType):
    class Meta:
        model = models.IndexDefinition
        interfaces = (relay.Node,)


class IndexValueType(SQLAlchemyObjectType):
    class Meta:
        model = models.IndexValue
        interfaces = (relay.Node,)


class IndexConstituentType(SQLAlchemyObjectType):
    class Meta:
        model = models.IndexConstituent
        interfaces = (relay.Node,)


class Query(graphene.ObjectType):
    # Securities
    securities = SQLAlchemyConnectionField(SecurityType)
    security = graphene.Field(SecurityType, id=graphene.Int(), symbol=graphene.String())
    
    # Price Data
    price_data = SQLAlchemyConnectionField(PriceDataType)
    latest_price = graphene.Field(PriceDataType, symbol=graphene.String(required=True))
    
    # Indices
    indices = SQLAlchemyConnectionField(IndexDefinitionType)
    index = graphene.Field(IndexDefinitionType, id=graphene.Int())
    index_values = SQLAlchemyConnectionField(IndexValueType, index_id=graphene.Int())
    
    def resolve_security(self, info, id=None, symbol=None):
        """Resolve security by ID or symbol"""
        db = next(get_db())
        query = db.query(models.Security)
        
        if id:
            return query.filter(models.Security.id == id).first()
        elif symbol:
            return query.filter(models.Security.symbol == symbol).first()
        
        return None
    
    def resolve_latest_price(self, info, symbol):
        """Resolve latest price for a symbol"""
        db = next(get_db())
        
        # Get security by symbol
        security = db.query(models.Security).filter(models.Security.symbol == symbol).first()
        if not security:
            return None
        
        # Get latest price
        return db.query(models.PriceData).filter(
            models.PriceData.security_id == security.id
        ).order_by(models.PriceData.date.desc()).first()
    
    def resolve_index(self, info, id):
        """Resolve index by ID"""
        db = next(get_db())
        return db.query(models.IndexDefinition).filter(models.IndexDefinition.id == id).first()
    
    def resolve_index_values(self, info, index_id=None):
        """Resolve index values"""
        db = next(get_db())
        query = db.query(models.IndexValue)
        
        if index_id:
            query = query.filter(models.IndexValue.index_definition_id == index_id)
        
        return query.order_by(models.IndexValue.date.desc()).all()


class CreateSecurityInput(graphene.InputObjectType):
    symbol = graphene.String(required=True)
    name = graphene.String(required=True)
    exchange = graphene.String()
    currency = graphene.String()
    sector = graphene.String()
    industry = graphene.String()
    country = graphene.String()
    market_cap = graphene.Float()


class CreateSecurity(graphene.Mutation):
    class Arguments:
        input = CreateSecurityInput(required=True)
    
    security = graphene.Field(SecurityType)
    
    def mutate(self, info, input):
        db = next(get_db())
        
        # Check if security already exists
        existing = db.query(models.Security).filter(models.Security.symbol == input.symbol).first()
        if existing:
            raise Exception("Security with this symbol already exists")
        
        security = models.Security(
            symbol=input.symbol,
            name=input.name,
            exchange=input.exchange,
            currency=input.currency or "USD",
            sector=input.sector,
            industry=input.industry,
            country=input.country,
            market_cap=input.market_cap
        )
        
        db.add(security)
        db.commit()
        db.refresh(security)
        
        return CreateSecurity(security=security)


class CreateIndexDefinitionInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    description = graphene.String()
    weighting_method = graphene.String(required=True)
    rebalance_frequency = graphene.String()
    max_constituents = graphene.Int()
    min_market_cap = graphene.Float()
    max_market_cap = graphene.Float()
    sectors = graphene.String()
    countries = graphene.String()
    esg_criteria = graphene.String()


class CreateIndexDefinition(graphene.Mutation):
    class Arguments:
        input = CreateIndexDefinitionInput(required=True)
    
    index_definition = graphene.Field(IndexDefinitionType)
    
    def mutate(self, info, input):
        db = next(get_db())
        
        # Check if index already exists
        existing = db.query(models.IndexDefinition).filter(
            models.IndexDefinition.name == input.name
        ).first()
        if existing:
            raise Exception("Index with this name already exists")
        
        index_definition = models.IndexDefinition(
            name=input.name,
            description=input.description,
            weighting_method=input.weighting_method,
            rebalance_frequency=input.rebalance_frequency or "monthly",
            max_constituents=input.max_constituents,
            min_market_cap=input.min_market_cap,
            max_market_cap=input.max_market_cap,
            sectors=input.sectors,
            countries=input.countries,
            esg_criteria=input.esg_criteria
        )
        
        db.add(index_definition)
        db.commit()
        db.refresh(index_definition)
        
        return CreateIndexDefinition(index_definition=index_definition)


class Mutation(graphene.ObjectType):
    create_security = CreateSecurity.Field()
    create_index_definition = CreateIndexDefinition.Field()


# Create GraphQL schema
schema = graphene.Schema(query=Query, mutation=Mutation)


# Create FastAPI app for GraphQL
from fastapi import FastAPI
from starlette.graphql import GraphQLApp

graphql_app = GraphQLApp(schema=schema)
