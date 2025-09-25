"""
API v1 router
"""
from fastapi import APIRouter

from app.api.api_v1.endpoints import securities, indices, prices, ingestion, users, auth

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(securities.router, prefix="/securities", tags=["securities"])
api_router.include_router(indices.router, prefix="/indices", tags=["indices"])
api_router.include_router(prices.router, prefix="/prices", tags=["prices"])
api_router.include_router(ingestion.router, prefix="/ingestion", tags=["ingestion"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
