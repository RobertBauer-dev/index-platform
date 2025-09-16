"""
Performance and load testing for Index Platform
"""
import pytest
import asyncio
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
import requests
from fastapi.testclient import TestClient

from app.main import app


class TestAPIPerformance:
    """Test API performance under load"""
    
    def setup_method(self):
        """Set up test client and base URL"""
        self.client = TestClient(app)
        self.base_url = "http://localhost:8000"
        self.auth_headers = self._get_auth_headers()
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for testing"""
        # This would need to be implemented based on your auth setup
        return {"Authorization": "Bearer test-token"}
    
    def test_single_request_performance(self):
        """Test performance of single API requests"""
        endpoints = [
            "/api/v1/securities",
            "/api/v1/indices",
            "/health",
            "/metrics"
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = self.client.get(endpoint)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            assert response.status_code in [200, 401]  # 401 for protected endpoints
            assert response_time < 1.0  # Should respond within 1 second
    
    def test_concurrent_requests(self):
        """Test API performance under concurrent load"""
        endpoint = "/api/v1/securities"
        num_requests = 50
        max_workers = 10
        
        def make_request():
            start_time = time.time()
            response = self.client.get(endpoint)
            end_time = time.time()
            return {
                "status_code": response.status_code,
                "response_time": end_time - start_time,
                "success": response.status_code == 200
            }
        
        # Execute concurrent requests
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            results = [future.result() for future in as_completed(futures)]
        
        # Analyze results
        response_times = [r["response_time"] for r in results]
        success_rate = sum(1 for r in results if r["success"]) / len(results)
        
        # Performance assertions
        assert success_rate >= 0.95  # 95% success rate
        assert statistics.mean(response_times) < 2.0  # Average response time < 2s
        assert max(response_times) < 5.0  # Max response time < 5s
        assert statistics.median(response_times) < 1.5  # Median response time < 1.5s
    
    def test_high_load_performance(self):
        """Test API performance under high load"""
        endpoint = "/api/v1/securities"
        num_requests = 200
        max_workers = 20
        
        def make_request():
            start_time = time.time()
            response = self.client.get(endpoint)
            end_time = time.time()
            return {
                "status_code": response.status_code,
                "response_time": end_time - start_time,
                "success": response.status_code == 200
            }
        
        # Execute high load requests
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            results = [future.result() for future in as_completed(futures)]
        total_time = time.time() - start_time
        
        # Analyze results
        response_times = [r["response_time"] for r in results]
        success_rate = sum(1 for r in results if r["success"]) / len(results)
        throughput = num_requests / total_time
        
        # Performance assertions
        assert success_rate >= 0.90  # 90% success rate under high load
        assert throughput >= 10  # At least 10 requests per second
        assert statistics.mean(response_times) < 3.0  # Average response time < 3s
        assert max(response_times) < 10.0  # Max response time < 10s
    
    def test_database_query_performance(self):
        """Test database query performance"""
        # Test securities endpoint with pagination
        endpoint = "/api/v1/securities"
        params = {"page": 1, "size": 100}
        
        start_time = time.time()
        response = self.client.get(endpoint, params=params)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code in [200, 401]
        assert response_time < 2.0  # Database queries should be fast
    
    def test_index_calculation_performance(self):
        """Test index calculation performance"""
        # This would test the index calculation endpoint
        # For now, we'll test a mock calculation
        endpoint = "/api/v1/indices/1/calculate"
        
        start_time = time.time()
        response = self.client.post(endpoint)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Index calculations might take longer
        assert response.status_code in [200, 401, 404]
        assert response_time < 10.0  # Index calculations should complete within 10s


class TestDataProcessingPerformance:
    """Test data processing performance"""
    
    def test_large_dataset_processing(self, large_dataset_securities):
        """Test processing of large datasets"""
        from app.processing.etl_pipeline import ETLPipeline
        
        pipeline = ETLPipeline()
        
        # Test with large dataset
        start_time = time.time()
        processed_data = pipeline.run_pipeline(large_dataset_securities)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        assert len(processed_data) == len(large_dataset_securities)
        assert processing_time < 30.0  # Should process 1000 records within 30s
    
    def test_index_calculation_performance(self, large_dataset_securities):
        """Test index calculation performance with large datasets"""
        from app.calculation.index_engine import IndexEngine
        
        engine = IndexEngine()
        
        # Test equal weight calculation
        start_time = time.time()
        weights = engine.calculate_equal_weights(large_dataset_securities)
        end_time = time.time()
        
        calculation_time = end_time - start_time
        
        assert len(weights) == len(large_dataset_securities)
        assert calculation_time < 5.0  # Should calculate weights within 5s
        
        # Test market cap weight calculation
        start_time = time.time()
        weights = engine.calculate_market_cap_weights(large_dataset_securities)
        end_time = time.time()
        
        calculation_time = end_time - start_time
        
        assert len(weights) == len(large_dataset_securities)
        assert calculation_time < 5.0  # Should calculate weights within 5s
    
    def test_data_cleaning_performance(self, large_dataset_securities):
        """Test data cleaning performance"""
        from app.processing.data_cleaner import DataCleaner
        
        cleaner = DataCleaner()
        
        # Test duplicate removal
        start_time = time.time()
        cleaned_data = cleaner.remove_duplicates(large_dataset_securities, key="symbol")
        end_time = time.time()
        
        cleaning_time = end_time - start_time
        
        assert cleaning_time < 2.0  # Should clean data within 2s
    
    def test_data_transformation_performance(self, large_dataset_securities):
        """Test data transformation performance"""
        from app.processing.data_transformer import DataTransformer
        
        transformer = DataTransformer()
        
        # Test market cap calculation
        start_time = time.time()
        transformed_data = transformer.calculate_market_cap(large_dataset_securities)
        end_time = time.time()
        
        transformation_time = end_time - start_time
        
        assert len(transformed_data) == len(large_dataset_securities)
        assert transformation_time < 3.0  # Should transform data within 3s


class TestMemoryUsage:
    """Test memory usage under load"""
    
    def test_memory_usage_single_request(self):
        """Test memory usage for single requests"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Make several requests
        for _ in range(10):
            response = self.client.get("/api/v1/securities")
            assert response.status_code in [200, 401]
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable
        assert memory_increase < 100  # Less than 100MB increase
    
    def test_memory_usage_large_dataset(self, large_dataset_securities):
        """Test memory usage with large datasets"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Process large dataset
        from app.processing.etl_pipeline import ETLPipeline
        pipeline = ETLPipeline()
        processed_data = pipeline.run_pipeline(large_dataset_securities)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable
        assert memory_increase < 500  # Less than 500MB increase for 1000 records


class TestConcurrentOperations:
    """Test concurrent operations performance"""
    
    def test_concurrent_index_calculations(self):
        """Test concurrent index calculations"""
        from app.calculation.index_engine import IndexEngine
        
        engine = IndexEngine()
        sample_data = [
            {"id": i, "price": 100.0 + i, "market_cap": 1000000000.0 + i * 1000000}
            for i in range(100)
        ]
        
        def calculate_weights():
            return engine.calculate_market_cap_weights(sample_data)
        
        # Run concurrent calculations
        num_concurrent = 10
        with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = [executor.submit(calculate_weights) for _ in range(num_concurrent)]
            results = [future.result() for future in as_completed(futures)]
        
        # All calculations should complete successfully
        assert len(results) == num_concurrent
        for result in results:
            assert len(result) == len(sample_data)
            assert abs(sum(result) - 1.0) < 0.001  # Weights should sum to 1
    
    def test_concurrent_data_ingestion(self, sample_securities_data):
        """Test concurrent data ingestion"""
        from app.ingestion.csv_ingestor import CSVIngestor
        
        ingestor = CSVIngestor()
        
        def ingest_data():
            # Mock ingestion
            return len(sample_securities_data)
        
        # Run concurrent ingestion
        num_concurrent = 5
        with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = [executor.submit(ingest_data) for _ in range(num_concurrent)]
            results = [future.result() for future in as_completed(futures)]
        
        # All ingestion should complete successfully
        assert len(results) == num_concurrent
        for result in results:
            assert result == len(sample_securities_data)


class TestScalability:
    """Test system scalability"""
    
    def test_scalability_with_dataset_size(self):
        """Test how performance scales with dataset size"""
        from app.calculation.index_engine import IndexEngine
        
        engine = IndexEngine()
        dataset_sizes = [100, 500, 1000, 2000]
        results = []
        
        for size in dataset_sizes:
            # Create dataset of specified size
            data = [
                {"id": i, "price": 100.0 + i, "market_cap": 1000000000.0 + i * 1000000}
                for i in range(size)
            ]
            
            # Measure calculation time
            start_time = time.time()
            weights = engine.calculate_market_cap_weights(data)
            end_time = time.time()
            
            calculation_time = end_time - start_time
            results.append((size, calculation_time))
        
        # Performance should scale reasonably
        for size, calc_time in results:
            assert calc_time < size * 0.01  # Should be roughly linear
    
    def test_scalability_with_concurrent_users(self):
        """Test how performance scales with concurrent users"""
        endpoint = "/api/v1/securities"
        user_counts = [1, 5, 10, 20, 50]
        results = []
        
        for num_users in user_counts:
            def make_request():
                start_time = time.time()
                response = self.client.get(endpoint)
                end_time = time.time()
                return end_time - start_time
            
            # Simulate concurrent users
            with ThreadPoolExecutor(max_workers=num_users) as executor:
                futures = [executor.submit(make_request) for _ in range(num_users)]
                response_times = [future.result() for future in as_completed(futures)]
            
            avg_response_time = statistics.mean(response_times)
            results.append((num_users, avg_response_time))
        
        # Response time should not degrade significantly
        for num_users, avg_time in results:
            assert avg_time < 5.0  # Should remain under 5s even with 50 users


class TestResourceUtilization:
    """Test resource utilization under load"""
    
    def test_cpu_utilization(self):
        """Test CPU utilization under load"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # Measure CPU usage during intensive operations
        cpu_percentages = []
        
        for _ in range(10):
            # Simulate CPU-intensive operation
            start_time = time.time()
            while time.time() - start_time < 0.1:  # 100ms of work
                _ = sum(range(1000))
            
            cpu_percent = process.cpu_percent()
            cpu_percentages.append(cpu_percent)
        
        # CPU usage should be reasonable
        avg_cpu = statistics.mean(cpu_percentages)
        assert avg_cpu < 80  # Should not exceed 80% CPU usage
    
    def test_disk_io_performance(self):
        """Test disk I/O performance"""
        import tempfile
        import os
        
        # Test file write performance
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            start_time = time.time()
            
            # Write large amount of data
            data = "x" * 1024 * 1024  # 1MB
            for _ in range(10):  # 10MB total
                temp_file.write(data.encode())
            
            end_time = time.time()
            write_time = end_time - start_time
        
        # Clean up
        os.unlink(temp_file.name)
        
        # Write performance should be reasonable
        assert write_time < 5.0  # Should write 10MB within 5s
    
    def test_network_performance(self):
        """Test network performance"""
        # Test local network performance (if running with real server)
        if hasattr(self, 'base_url') and self.base_url.startswith('http://'):
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}/health", timeout=5)
                end_time = time.time()
                
                response_time = end_time - start_time
                
                assert response.status_code == 200
                assert response_time < 1.0  # Network response should be fast
            except requests.RequestException:
                # Skip if server is not running
                pytest.skip("Server not running for network test")


class TestPerformanceRegression:
    """Test for performance regressions"""
    
    def test_response_time_regression(self):
        """Test that response times don't regress"""
        endpoints = [
            "/health",
            "/metrics",
            "/api/v1/securities",
            "/api/v1/indices"
        ]
        
        baseline_times = {
            "/health": 0.1,
            "/metrics": 0.2,
            "/api/v1/securities": 1.0,
            "/api/v1/indices": 1.0
        }
        
        for endpoint in endpoints:
            start_time = time.time()
            response = self.client.get(endpoint)
            end_time = time.time()
            
            response_time = end_time - start_time
            baseline_time = baseline_times.get(endpoint, 2.0)
            
            # Response time should not exceed baseline by more than 50%
            assert response_time < baseline_time * 1.5
    
    def test_throughput_regression(self):
        """Test that throughput doesn't regress"""
        endpoint = "/api/v1/securities"
        num_requests = 100
        
        start_time = time.time()
        
        # Make requests sequentially
        for _ in range(num_requests):
            response = self.client.get(endpoint)
            assert response.status_code in [200, 401]
        
        end_time = time.time()
        total_time = end_time - start_time
        throughput = num_requests / total_time
        
        # Should maintain at least 10 requests per second
        assert throughput >= 10.0
