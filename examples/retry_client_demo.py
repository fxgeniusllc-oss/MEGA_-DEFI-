"""Example: Using Retry Client for API Calls with Exponential Backoff.

This example demonstrates how to use the retry client to handle
rate-limited API calls with automatic retry and exponential backoff.
"""

import time
from mega_defi.core.retry_client import RetryClient, RetryConfig, RetryError, with_retry


def example_basic_retry():
    """Basic retry example."""
    print("=" * 60)
    print("Example 1: Basic Retry")
    print("=" * 60)
    
    attempt_count = [0]
    
    def flaky_operation():
        """Simulates a flaky operation that succeeds on 3rd attempt."""
        attempt_count[0] += 1
        print(f"  Attempt {attempt_count[0]}")
        
        if attempt_count[0] < 3:
            raise Exception("Temporary failure")
        
        return "Success!"
    
    # Use convenience function
    try:
        result = with_retry(flaky_operation, RetryConfig(max_retries=5))
        print(f"✓ Result: {result}")
    except RetryError as e:
        print(f"✗ Failed after {e.attempts} attempts: {e.last_error}")
    
    print()


def example_rate_limited_api():
    """Example handling rate-limited API."""
    print("=" * 60)
    print("Example 2: Rate-Limited API")
    print("=" * 60)
    
    call_count = [0]
    
    def rate_limited_api():
        """Simulates a rate-limited API."""
        call_count[0] += 1
        print(f"  API Call {call_count[0]}")
        
        if call_count[0] < 4:
            error = Exception("Rate limit exceeded")
            error.status = 429  # type: ignore
            raise error
        
        return {"data": "API Response"}
    
    # Configure client for rate-limited APIs
    client = RetryClient(RetryConfig(
        max_retries=10,
        base_delay_ms=1000,
        backoff_multiplier=2.0,
        retryable_status_codes=[429]
    ))
    
    try:
        start_time = time.time()
        result = client.execute_with_retry(rate_limited_api)
        elapsed = time.time() - start_time
        print(f"✓ Success after {elapsed:.2f}s: {result}")
    except RetryError as e:
        print(f"✗ Failed: {e}")
    
    print()


def example_custom_configuration():
    """Example with custom retry configuration."""
    print("=" * 60)
    print("Example 3: Custom Configuration")
    print("=" * 60)
    
    # Custom configuration for aggressive retry
    config = RetryConfig(
        max_retries=5,
        base_delay_ms=500,
        max_delay_ms=10000,
        backoff_multiplier=3.0
    )
    
    client = RetryClient(config)
    
    attempts = [0]
    
    def operation():
        attempts[0] += 1
        if attempts[0] < 3:
            raise ConnectionError("Network issue")
        return "Connected"
    
    try:
        result = client.execute_with_retry(operation)
        print(f"✓ Result: {result}")
        print(f"  Total attempts: {attempts[0]}")
    except RetryError as e:
        print(f"✗ Failed: {e}")
    
    print()


def example_http_fetch():
    """Example HTTP fetch with retry."""
    print("=" * 60)
    print("Example 4: HTTP Fetch (Simulated)")
    print("=" * 60)
    
    # Note: This is a simulation. Real usage would make actual HTTP requests.
    
    class MockResponse:
        def __init__(self, status_code, ok):
            self.status_code = status_code
            self.ok = ok
            self.reason = "Rate Limited" if status_code == 429 else "OK"
        
        def raise_for_status(self):
            if not self.ok:
                raise Exception(f"HTTP {self.status_code}")
    
    # Simulate HTTP library
    import sys
    from unittest.mock import Mock
    
    # Mock requests module
    mock_requests = Mock()
    call_count = [0]
    
    def mock_request(**kwargs):
        call_count[0] += 1
        print(f"  HTTP Request {call_count[0]}")
        if call_count[0] < 3:
            return MockResponse(429, False)
        return MockResponse(200, True)
    
    mock_requests.request = mock_request
    sys.modules['requests'] = mock_requests
    
    client = RetryClient(RetryConfig(
        max_retries=5,
        base_delay_ms=500
    ))
    
    try:
        response = client.fetch_with_retry(
            url='https://api.example.com/data',
            method='GET',
            headers={'Authorization': 'Bearer token'}
        )
        print(f"✓ HTTP {response.status_code}: Success")
    except Exception as e:
        print(f"✗ Failed: {e}")
    finally:
        # Clean up mock
        del sys.modules['requests']
    
    print()


def example_error_handling():
    """Example error handling and retry decisions."""
    print("=" * 60)
    print("Example 5: Error Handling")
    print("=" * 60)
    
    def non_retryable_error():
        """Operation that raises non-retryable error."""
        raise ValueError("Invalid input - should not retry")
    
    def retryable_error():
        """Operation that raises retryable error."""
        error = Exception("Service unavailable")
        error.status = 503  # type: ignore
        raise error
    
    client = RetryClient(RetryConfig(max_retries=3))
    
    # Non-retryable error
    print("  Testing non-retryable error...")
    try:
        client.execute_with_retry(non_retryable_error)
    except ValueError as e:
        print(f"  ✓ Correctly failed immediately: {e}")
    except RetryError:
        print(f"  ✗ Should not have retried")
    
    # Retryable error
    print("\n  Testing retryable error...")
    try:
        client.execute_with_retry(retryable_error)
    except RetryError as e:
        print(f"  ✓ Correctly retried {e.attempts} times before failing")
    
    print()


def example_copilot_api():
    """Example for Copilot API integration."""
    print("=" * 60)
    print("Example 6: Copilot API Integration")
    print("=" * 60)
    
    print("Configuration for Copilot API:")
    
    config = RetryConfig(
        max_retries=10,           # Retry up to 10 times
        base_delay_ms=2000,       # Start with 2 second delay
        max_delay_ms=60000,       # Cap at 60 seconds
        backoff_multiplier=2.0,   # Double delay each time
        retryable_status_codes=[408, 429, 500, 502, 503, 504],
        retryable_errors=['rate_limited', 'too_many_requests']
    )
    
    print(f"  Max Retries: {config.max_retries}")
    print(f"  Base Delay: {config.base_delay_ms}ms")
    print(f"  Max Delay: {config.max_delay_ms}ms")
    print(f"  Backoff Multiplier: {config.backoff_multiplier}")
    print(f"  Retryable Status Codes: {config.retryable_status_codes}")
    print(f"  Retryable Errors: {config.retryable_errors}")
    
    print("\nExpected delay progression:")
    client = RetryClient(config)
    for i in range(5):
        delay = client._calculate_delay(i, config)
        print(f"  Attempt {i+1}: ~{delay}ms")
    
    print("\n✓ Use this configuration for Copilot API calls")
    print()


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "RETRY CLIENT EXAMPLES" + " " * 27 + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    example_basic_retry()
    example_rate_limited_api()
    example_custom_configuration()
    example_http_fetch()
    example_error_handling()
    example_copilot_api()
    
    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)
    print()
    print("See RETRY_BACKOFF_GUIDE.md for detailed usage documentation")
    print()


if __name__ == '__main__':
    main()
