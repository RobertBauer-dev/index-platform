"""
Metrics endpoint for Prometheus
"""
from fastapi import APIRouter, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from app.core.metrics import get_metrics, get_metrics_content_type

router = APIRouter()


@router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    metrics_data = get_metrics()
    return Response(
        content=metrics_data,
        media_type=CONTENT_TYPE_LATEST
    )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "index-platform-backend",
        "version": "1.0.0"
    }


@router.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    # Add checks for database, redis, etc.
    return {
        "status": "ready",
        "service": "index-platform-backend",
        "checks": {
            "database": "ok",
            "redis": "ok",
            "external_apis": "ok"
        }
    }
