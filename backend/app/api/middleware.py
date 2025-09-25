"""
Middleware for metrics collection and monitoring
"""
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging

from app.core.metrics import metrics_collector

logger = logging.getLogger(__name__)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect HTTP metrics"""
    
    def __init__(self, app):
        super().__init__(app)
        self._active_connections = 0
    
    async def dispatch(self, request: Request, call_next):
        # Increment active connections
        self._active_connections += 1
        
        # Record request start time
        start_time = time.time()
        
        # Process request
        try:
            response = await call_next(request)
            
            # Record metrics using the existing metrics collector
            duration = time.time() - start_time
            metrics_collector.record_http_request(request, response, duration)
            
            return response
            
        except Exception as e:
            # Record error metrics
            duration = time.time() - start_time
            method = request.method
            endpoint = request.url.path
            
            logger.error(f"Request failed: {method} {endpoint} - {str(e)}")
            raise e
            
        finally:
            # Decrement active connections
            self._active_connections -= 1


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        # Process request
        response = await call_next(request)
        
        # Log response
        duration = time.time() - start_time
        logger.info(
            f"Response: {request.method} {request.url.path} "
            f"- {response.status_code} - {duration:.3f}s"
        )
        
        return response


class SecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware for headers and rate limiting"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response


class DatabaseMetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect database metrics"""
    
    async def dispatch(self, request: Request, call_next):
        # This would integrate with SQLAlchemy events
        # to track database query metrics
        response = await call_next(request)
        return response
