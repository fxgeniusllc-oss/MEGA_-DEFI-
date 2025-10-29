"""Tests for Retry Client with Exponential Backoff."""

import unittest
import time
from mega_defi.core.retry_client import (
    RetryClient,
    RetryConfig,
    RetryError,
    with_retry
)


class TestRetryConfig(unittest.TestCase):
    """Test cases for RetryConfig."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = RetryConfig()
        self.assertEqual(config.max_retries, 5)
        self.assertEqual(config.base_delay_ms, 1000)
        self.assertEqual(config.max_delay_ms, 32000)
        self.assertEqual(config.backoff_multiplier, 2.0)
        self.assertIn(429, config.retryable_status_codes)
        self.assertIn('rate_limited', config.retryable_errors)
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = RetryConfig(
            max_retries=3,
            base_delay_ms=500,
            max_delay_ms=10000,
            backoff_multiplier=3.0
        )
        self.assertEqual(config.max_retries, 3)
        self.assertEqual(config.base_delay_ms, 500)
        self.assertEqual(config.max_delay_ms, 10000)
        self.assertEqual(config.backoff_multiplier, 3.0)


class TestRetryClient(unittest.TestCase):
    """Test cases for RetryClient."""
    
    def test_successful_operation(self):
        """Test operation that succeeds on first try."""
        client = RetryClient()
        
        def successful_operation():
            return "success"
        
        result = client.execute_with_retry(successful_operation)
        self.assertEqual(result, "success")
    
    def test_retry_on_transient_error(self):
        """Test retry on transient error."""
        client = RetryClient(RetryConfig(
            max_retries=5,
            base_delay_ms=100
        ))
        
        attempts = [0]
        
        def flaky_operation():
            attempts[0] += 1
            if attempts[0] < 3:
                raise ConnectionError("Temporary failure")
            return "success"
        
        result = client.execute_with_retry(flaky_operation)
        self.assertEqual(result, "success")
        self.assertEqual(attempts[0], 3)
    
    def test_retry_exhausted(self):
        """Test that retries are exhausted after max attempts."""
        client = RetryClient(RetryConfig(
            max_retries=3,
            base_delay_ms=100
        ))
        
        attempts = [0]
        
        def always_failing_operation():
            attempts[0] += 1
            raise ConnectionError("Always fails")
        
        with self.assertRaises(RetryError) as context:
            client.execute_with_retry(always_failing_operation)
        
        self.assertEqual(context.exception.attempts, 3)
        self.assertEqual(attempts[0], 3)
        self.assertIsInstance(context.exception.last_error, ConnectionError)
    
    def test_non_retryable_error(self):
        """Test that non-retryable errors fail immediately."""
        client = RetryClient(RetryConfig(max_retries=5))
        
        attempts = [0]
        
        def invalid_operation():
            attempts[0] += 1
            raise ValueError("Invalid input")
        
        with self.assertRaises(ValueError):
            client.execute_with_retry(invalid_operation)
        
        # Should fail immediately without retries
        self.assertEqual(attempts[0], 1)
    
    def test_rate_limit_retry(self):
        """Test retry on rate limit error."""
        client = RetryClient(RetryConfig(
            max_retries=5,
            base_delay_ms=100
        ))
        
        attempts = [0]
        
        def rate_limited_operation():
            attempts[0] += 1
            if attempts[0] < 3:
                error = Exception("Rate limit exceeded")
                error.status = 429  # type: ignore
                raise error
            return "success"
        
        result = client.execute_with_retry(rate_limited_operation)
        self.assertEqual(result, "success")
        self.assertGreaterEqual(attempts[0], 3)
    
    def test_exponential_backoff(self):
        """Test exponential backoff delay calculation."""
        config = RetryConfig(
            base_delay_ms=1000,
            max_delay_ms=32000,
            backoff_multiplier=2.0
        )
        client = RetryClient(config)
        
        # Test delay progression
        delay0 = client._calculate_delay(0, config)
        delay1 = client._calculate_delay(1, config)
        delay2 = client._calculate_delay(2, config)
        
        # Verify exponential growth (with jitter tolerance)
        self.assertGreater(delay1, delay0)
        self.assertGreater(delay2, delay1)
        
        # Verify delays are within reasonable bounds
        self.assertGreaterEqual(delay0, 800)  # With jitter
        self.assertLessEqual(delay0, 1200)
        
        # Verify max delay cap
        delay_large = client._calculate_delay(10, config)
        self.assertLessEqual(delay_large, config.max_delay_ms)
    
    def test_with_retry_convenience_function(self):
        """Test convenience function for retry."""
        attempts = [0]
        
        def operation():
            attempts[0] += 1
            if attempts[0] < 2:
                raise ConnectionError("Temporary error")
            return "success"
        
        result = with_retry(operation, RetryConfig(
            max_retries=3,
            base_delay_ms=100
        ))
        
        self.assertEqual(result, "success")
        self.assertEqual(attempts[0], 2)
    
    def test_config_update(self):
        """Test updating client configuration."""
        client = RetryClient(RetryConfig(max_retries=3))
        
        self.assertEqual(client.get_config().max_retries, 3)
        
        client.update_config(max_retries=5)
        
        self.assertEqual(client.get_config().max_retries, 5)
    
    def test_context_override(self):
        """Test context override for single execution."""
        client = RetryClient(RetryConfig(
            max_retries=3,
            base_delay_ms=1000
        ))
        
        attempts = [0]
        
        def operation():
            attempts[0] += 1
            if attempts[0] < 4:
                raise ConnectionError("Temporary error")
            return "success"
        
        # Should succeed with override
        result = client.execute_with_retry(
            operation,
            {'max_retries': 5, 'base_delay_ms': 100}
        )
        
        self.assertEqual(result, "success")
        self.assertEqual(attempts[0], 4)
        
        # Original config should be unchanged
        self.assertEqual(client.get_config().max_retries, 3)
    
    def test_error_message_detection(self):
        """Test retry on error message patterns."""
        client = RetryClient(RetryConfig(
            max_retries=3,
            base_delay_ms=100
        ))
        
        attempts = [0]
        
        def throttled_operation():
            attempts[0] += 1
            if attempts[0] < 2:
                raise Exception("You are being rate limited")
            return "success"
        
        result = client.execute_with_retry(throttled_operation)
        self.assertEqual(result, "success")
        self.assertGreaterEqual(attempts[0], 2)


class TestRetryError(unittest.TestCase):
    """Test cases for RetryError."""
    
    def test_retry_error_properties(self):
        """Test RetryError exception properties."""
        last_error = ValueError("Original error")
        retry_error = RetryError("Failed after retries", 5, last_error)
        
        self.assertEqual(retry_error.attempts, 5)
        self.assertEqual(retry_error.last_error, last_error)
        self.assertIn("Failed after retries", str(retry_error))


class TestRetryIntegration(unittest.TestCase):
    """Integration tests for retry client."""
    
    def test_realistic_api_scenario(self):
        """Test realistic API call scenario with rate limiting."""
        client = RetryClient(RetryConfig(
            max_retries=10,
            base_delay_ms=100,
            backoff_multiplier=2.0,
            retryable_status_codes=[429, 503]
        ))
        
        call_count = [0]
        
        def simulated_api_call():
            call_count[0] += 1
            
            # Simulate rate limiting for first few calls
            if call_count[0] <= 3:
                error = Exception("Rate limit exceeded")
                error.status = 429  # type: ignore
                raise error
            
            # Simulate service unavailable
            if call_count[0] == 4:
                error = Exception("Service temporarily unavailable")
                error.status = 503  # type: ignore
                raise error
            
            # Success after retries
            return {"data": "Success", "attempt": call_count[0]}
        
        start_time = time.time()
        result = client.execute_with_retry(simulated_api_call)
        elapsed = time.time() - start_time
        
        self.assertEqual(result["data"], "Success")
        self.assertEqual(call_count[0], 5)
        
        # Should have taken some time due to backoff
        self.assertGreater(elapsed, 0.3)  # At least 300ms with delays
    
    def test_mixed_error_types(self):
        """Test handling of mixed retryable and non-retryable errors."""
        client = RetryClient(RetryConfig(
            max_retries=5,
            base_delay_ms=100
        ))
        
        attempts = [0]
        
        def mixed_errors_operation():
            attempts[0] += 1
            
            if attempts[0] == 1:
                raise ConnectionError("Network issue")
            elif attempts[0] == 2:
                error = Exception("Rate limited")
                error.status = 429  # type: ignore
                raise error
            elif attempts[0] == 3:
                return "success"
            else:
                raise ValueError("Should not reach here")
        
        result = client.execute_with_retry(mixed_errors_operation)
        self.assertEqual(result, "success")
        self.assertEqual(attempts[0], 3)


if __name__ == '__main__':
    unittest.main()
