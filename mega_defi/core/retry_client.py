"""Retry Client with Exponential Backoff.

Provides a robust API client with automatic retry logic and exponential backoff
for handling rate limits and transient failures.
"""

import time
import logging
from typing import TypeVar, Callable, Any, Optional, List, Dict
from dataclasses import dataclass, field
import random

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_retries: int = 5
    base_delay_ms: int = 1000
    max_delay_ms: int = 32000
    backoff_multiplier: float = 2.0
    retryable_status_codes: List[int] = field(default_factory=lambda: [408, 429, 500, 502, 503, 504])
    retryable_errors: List[str] = field(default_factory=lambda: [
        'ConnectionResetError',
        'TimeoutError',
        'ConnectionError',
        'rate_limited',
        'too_many_requests'
    ])


class RetryError(Exception):
    """Exception raised when all retry attempts are exhausted."""
    
    def __init__(self, message: str, attempts: int, last_error: Optional[Exception] = None):
        super().__init__(message)
        self.attempts = attempts
        self.last_error = last_error


class RetryClient:
    """Client for executing operations with retry logic and exponential backoff."""
    
    def __init__(self, config: Optional[RetryConfig] = None):
        """
        Initialize retry client.
        
        Args:
            config: Retry configuration (uses defaults if None)
        """
        self.config = config or RetryConfig()
    
    def execute_with_retry(
        self,
        fn: Callable[[], T],
        context: Optional[Dict[str, Any]] = None
    ) -> T:
        """
        Execute a function with retry logic and exponential backoff.
        
        Args:
            fn: Function to execute
            context: Optional context to override config
            
        Returns:
            Result of function execution
            
        Raises:
            RetryError: If all retry attempts are exhausted
        """
        config = self._merge_config(context)
        last_error: Optional[Exception] = None
        
        for attempt in range(config.max_retries):
            try:
                return fn()
            except Exception as error:
                last_error = error
                
                # Check if we should retry
                if not self._should_retry(error, attempt, config):
                    raise
                
                # Calculate delay with exponential backoff
                delay_ms = self._calculate_delay(attempt, config)
                
                logger.warning(
                    f"Retry attempt {attempt + 1}/{config.max_retries} after {delay_ms}ms. "
                    f"Error: {str(error)}"
                )
                
                # Wait before retrying
                time.sleep(delay_ms / 1000.0)
        
        # All retries exhausted
        raise RetryError(
            f"Failed after {config.max_retries} retries",
            config.max_retries,
            last_error
        )
    
    def fetch_with_retry(
        self,
        url: str,
        method: str = 'GET',
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Any] = None,
        retry_config: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Execute an HTTP request with retry logic.
        
        Args:
            url: URL to fetch
            method: HTTP method
            headers: Request headers
            data: Request data
            retry_config: Optional retry configuration overrides
            
        Returns:
            Response object
            
        Raises:
            RetryError: If all retry attempts are exhausted
        """
        try:
            import requests
        except ImportError:
            raise ImportError("requests library is required for fetch_with_retry")
        
        def make_request():
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data
            )
            
            # Check if response status is retryable
            if not response.ok and self._is_retryable_status_code(response.status_code):
                error = Exception(f"HTTP {response.status_code}: {response.reason}")
                error.status = response.status_code  # type: ignore
                error.response = response  # type: ignore
                raise error
            
            response.raise_for_status()
            return response
        
        return self.execute_with_retry(make_request, retry_config)
    
    def _should_retry(
        self,
        error: Exception,
        attempt: int,
        config: RetryConfig
    ) -> bool:
        """
        Determine if an error should trigger a retry.
        
        Args:
            error: The exception that occurred
            attempt: Current attempt number (0-indexed)
            config: Retry configuration
            
        Returns:
            True if should retry, False otherwise
        """
        # Don't retry if we've exceeded max retries
        if attempt >= config.max_retries - 1:
            return False
        
        # Check for retryable HTTP status codes
        if hasattr(error, 'status') and self._is_retryable_status_code(
            error.status, config  # type: ignore
        ):
            return True
        
        # Check error type
        error_type = type(error).__name__
        if error_type in config.retryable_errors:
            return True
        
        # Check error message for rate limiting
        error_message = str(error).lower()
        if any(
            keyword in error_message
            for keyword in ['rate limit', 'too many requests', 'throttled']
        ):
            return True
        
        # Don't retry by default
        return False
    
    def _is_retryable_status_code(
        self,
        status_code: int,
        config: Optional[RetryConfig] = None
    ) -> bool:
        """Check if HTTP status code is retryable."""
        codes = (config or self.config).retryable_status_codes
        return status_code in codes
    
    def _calculate_delay(
        self,
        attempt: int,
        config: RetryConfig
    ) -> int:
        """
        Calculate delay with exponential backoff.
        
        Args:
            attempt: Current attempt number (0-indexed)
            config: Retry configuration
            
        Returns:
            Delay in milliseconds
        """
        # Exponential backoff: baseDelay * (multiplier ^ attempt)
        exponential_delay = config.base_delay_ms * (config.backoff_multiplier ** attempt)
        
        # Add jitter to prevent thundering herd (±20% randomization)
        jitter = exponential_delay * 0.2 * (random.random() - 0.5)
        
        # Cap at maximum delay
        return int(min(exponential_delay + jitter, config.max_delay_ms))
    
    def _merge_config(self, context: Optional[Dict[str, Any]]) -> RetryConfig:
        """Merge context overrides with base config."""
        if not context:
            return self.config
        
        return RetryConfig(
            max_retries=context.get('max_retries', self.config.max_retries),
            base_delay_ms=context.get('base_delay_ms', self.config.base_delay_ms),
            max_delay_ms=context.get('max_delay_ms', self.config.max_delay_ms),
            backoff_multiplier=context.get('backoff_multiplier', self.config.backoff_multiplier),
            retryable_status_codes=context.get('retryable_status_codes', self.config.retryable_status_codes),
            retryable_errors=context.get('retryable_errors', self.config.retryable_errors)
        )
    
    def get_config(self) -> RetryConfig:
        """Get current configuration."""
        return self.config
    
    def update_config(self, **kwargs: Any) -> None:
        """Update configuration."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)


# Create a default retry client instance
default_retry_client = RetryClient()


def with_retry(
    fn: Callable[[], T],
    config: Optional[RetryConfig] = None
) -> T:
    """
    Convenience function for executing with retry.
    
    Args:
        fn: Function to execute
        config: Optional retry configuration
        
    Returns:
        Result of function execution
        
    Example:
        >>> def api_call():
        ...     # Your API call here
        ...     return response
        >>> result = with_retry(api_call, RetryConfig(max_retries=3))
    """
    client = RetryClient(config)
    return client.execute_with_retry(fn)
