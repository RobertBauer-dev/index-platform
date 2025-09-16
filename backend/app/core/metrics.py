"""
Prometheus metrics for the Index Platform
"""
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
import time
from typing import Dict, Any


# HTTP Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0]
)

http_connections_active = Gauge(
    'http_connections_active',
    'Number of active HTTP connections'
)

# Business Metrics
index_calculations_total = Counter(
    'index_calculations_total',
    'Total index calculations performed',
    ['index_id', 'method']
)

index_calculation_duration_seconds = Histogram(
    'index_calculation_duration_seconds',
    'Index calculation duration in seconds',
    ['index_id', 'method'],
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 300.0]
)

index_calculation_errors_total = Counter(
    'index_calculation_errors_total',
    'Total index calculation errors',
    ['index_id', 'error_type']
)

data_ingestion_records_total = Counter(
    'data_ingestion_records_total',
    'Total records ingested',
    ['source', 'type']
)

data_ingestion_errors_total = Counter(
    'data_ingestion_errors_total',
    'Total data ingestion errors',
    ['source', 'error_type']
)

data_quality_score = Gauge(
    'data_quality_score',
    'Data quality score (0-100)',
    ['data_type']
)

# System Metrics
active_users_total = Gauge(
    'active_users_total',
    'Number of active users'
)

securities_total = Gauge(
    'securities_total',
    'Total number of securities'
)

indices_total = Gauge(
    'indices_total',
    'Total number of indices'
)

index_performance_total = Gauge(
    'index_performance_total',
    'Index performance metrics',
    ['index_id', 'metric_type']
)

# Database Metrics
db_connections_active = Gauge(
    'db_connections_active',
    'Number of active database connections'
)

db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['query_type'],
    buckets=[0.01, 0.1, 0.5, 1.0, 2.0, 5.0]
)

# Cache Metrics
cache_hits_total = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_type']
)

cache_misses_total = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_type']
)

cache_size_bytes = Gauge(
    'cache_size_bytes',
    'Cache size in bytes',
    ['cache_type']
)

# Application Info
app_info = Info(
    'app_info',
    'Application information'
)


class MetricsCollector:
    """Metrics collection and management"""
    
    def __init__(self):
        self.app_info.info({
            'version': '1.0.0',
            'name': 'index-platform',
            'environment': 'production'
        })
    
    def record_http_request(self, request: Request, response: Response, duration: float):
        """Record HTTP request metrics"""
        method = request.method
        endpoint = request.url.path
        status = str(response.status_code)
        
        http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=status
        ).inc()
        
        http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    def record_index_calculation(self, index_id: str, method: str, duration: float, success: bool = True):
        """Record index calculation metrics"""
        index_calculations_total.labels(
            index_id=index_id,
            method=method
        ).inc()
        
        index_calculation_duration_seconds.labels(
            index_id=index_id,
            method=method
        ).observe(duration)
        
        if not success:
            index_calculation_errors_total.labels(
                index_id=index_id,
                error_type='calculation_error'
            ).inc()
    
    def record_data_ingestion(self, source: str, record_type: str, count: int, success: bool = True):
        """Record data ingestion metrics"""
        data_ingestion_records_total.labels(
            source=source,
            type=record_type
        ).inc(count)
        
        if not success:
            data_ingestion_errors_total.labels(
                source=source,
                error_type='ingestion_error'
            ).inc()
    
    def update_data_quality_score(self, data_type: str, score: float):
        """Update data quality score"""
        data_quality_score.labels(data_type=data_type).set(score)
    
    def update_active_users(self, count: int):
        """Update active users count"""
        active_users_total.set(count)
    
    def update_securities_count(self, count: int):
        """Update securities count"""
        securities_total.set(count)
    
    def update_indices_count(self, count: int):
        """Update indices count"""
        indices_total.set(count)
    
    def record_db_query(self, query_type: str, duration: float):
        """Record database query metrics"""
        db_query_duration_seconds.labels(query_type=query_type).observe(duration)
    
    def record_cache_operation(self, cache_type: str, hit: bool):
        """Record cache operation metrics"""
        if hit:
            cache_hits_total.labels(cache_type=cache_type).inc()
        else:
            cache_misses_total.labels(cache_type=cache_type).inc()
    
    def update_cache_size(self, cache_type: str, size_bytes: int):
        """Update cache size"""
        cache_size_bytes.labels(cache_type=cache_type).set(size_bytes)


# Global metrics collector instance
metrics_collector = MetricsCollector()


def get_metrics() -> str:
    """Get Prometheus metrics in text format"""
    return generate_latest()


def get_metrics_content_type() -> str:
    """Get Prometheus metrics content type"""
    return CONTENT_TYPE_LATEST


# Context managers for timing operations
class Timer:
    """Context manager for timing operations"""
    
    def __init__(self, metric_func, *labels):
        self.metric_func = metric_func
        self.labels = labels
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            self.metric_func(*self.labels, duration)


# Decorators for automatic metrics collection
def track_http_requests(func):
    """Decorator to track HTTP request metrics"""
    async def wrapper(request: Request, *args, **kwargs):
        start_time = time.time()
        response = await func(request, *args, **kwargs)
        duration = time.time() - start_time
        
        metrics_collector.record_http_request(request, response, duration)
        return response
    
    return wrapper


def track_index_calculation(index_id: str, method: str):
    """Decorator to track index calculation metrics"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                metrics_collector.record_index_calculation(index_id, method, duration, success=True)
                return result
            except Exception as e:
                duration = time.time() - start_time
                metrics_collector.record_index_calculation(index_id, method, duration, success=False)
                raise e
        
        return wrapper
    return decorator


def track_data_ingestion(source: str, record_type: str):
    """Decorator to track data ingestion metrics"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                count = len(result) if isinstance(result, list) else 1
                metrics_collector.record_data_ingestion(source, record_type, count, success=True)
                return result
            except Exception as e:
                metrics_collector.record_data_ingestion(source, record_type, 0, success=False)
                raise e
        
        return wrapper
    return decorator
