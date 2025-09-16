"""
Main FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.api.api_v1.api import api_router
from app.api.metrics_endpoint import router as metrics_router
from app.api.middleware import MetricsMiddleware, LoggingMiddleware, SecurityMiddleware
from app.graphql.schema import graphql_app


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    await init_db()
    yield
    # Shutdown


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Index Platform",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(SecurityMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(MetricsMiddleware)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Host Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Include API Router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Include Metrics Router
app.include_router(metrics_router)

# Include GraphQL
app.mount("/graphql", graphql_app)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Index Platform API",
        "version": settings.VERSION,
        "docs": "/docs",
        "graphql": "/graphql"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
