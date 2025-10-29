# Retry and Backoff Logic Guide

This guide explains how to use the retry client utilities to handle API rate limits and transient failures with exponential backoff.

## Overview

The retry client provides:
- **Exponential backoff**: Increases wait time between retries exponentially
- **Configurable retry behavior**: Customize max retries, delays, and retry conditions
- **Rate limit handling**: Automatically retries when rate limited
- **Jitter**: Adds randomization to prevent thundering herd problem
- **Type-safe**: Full TypeScript and Python type support

## TypeScript Usage

### Basic Usage

```typescript
import { RetryClient, withRetry } from './src/core/retryClient';

// Using the convenience function
const result = await withRetry(async () => {
  // Your API call here
  const response = await fetch('https://api.example.com/data');
  return response.json();
});

// Using the client directly
const client = new RetryClient({
  maxRetries: 5,
  baseDelayMs: 1000,
  backoffMultiplier: 2
});

const data = await client.executeWithRetry(async () => {
  // Your operation
  return await someApiCall();
});
```

### HTTP Requests with Retry

```typescript
import { RetryClient } from './src/core/retryClient';

const client = new RetryClient();

// Fetch with automatic retry
const response = await client.fetchWithRetry(
  'https://api.example.com/endpoint',
  {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ key: 'value' })
  }
);
```

### Custom Configuration

```typescript
import { RetryClient, RetryConfig } from './src/core/retryClient';

const config: RetryConfig = {
  maxRetries: 3,                    // Maximum number of retry attempts
  baseDelayMs: 2000,                // Initial delay in milliseconds
  maxDelayMs: 30000,                // Maximum delay cap
  backoffMultiplier: 2,             // Exponential multiplier
  retryableStatusCodes: [429, 503], // HTTP status codes to retry
  retryableErrors: ['rate_limited'] // Error codes to retry
};

const client = new RetryClient(config);
```

### Handling Specific Errors

```typescript
import { RetryClient, RetryError } from './src/core/retryClient';

const client = new RetryClient();

try {
  const result = await client.executeWithRetry(async () => {
    // Your API call
    return await copilotApiCall();
  });
} catch (error) {
  if (error instanceof RetryError) {
    console.error(`Failed after ${error.attempts} attempts`);
    console.error('Last error:', error.lastError);
  } else {
    // Non-retryable error
    console.error('Fatal error:', error);
  }
}
```

## Python Usage

### Basic Usage

```python
from mega_defi.core.retry_client import RetryClient, with_retry, RetryConfig

# Using the convenience function
def api_call():
    # Your API call here
    response = requests.get('https://api.example.com/data')
    return response.json()

result = with_retry(api_call)

# Using the client directly
client = RetryClient(RetryConfig(
    max_retries=5,
    base_delay_ms=1000,
    backoff_multiplier=2.0
))

data = client.execute_with_retry(lambda: some_api_call())
```

### HTTP Requests with Retry

```python
from mega_defi.core.retry_client import RetryClient

client = RetryClient()

# Fetch with automatic retry
response = client.fetch_with_retry(
    url='https://api.example.com/endpoint',
    method='POST',
    headers={'Content-Type': 'application/json'},
    data={'key': 'value'}
)
```

### Custom Configuration

```python
from mega_defi.core.retry_client import RetryClient, RetryConfig

config = RetryConfig(
    max_retries=3,                     # Maximum number of retry attempts
    base_delay_ms=2000,                # Initial delay in milliseconds
    max_delay_ms=30000,                # Maximum delay cap
    backoff_multiplier=2.0,            # Exponential multiplier
    retryable_status_codes=[429, 503], # HTTP status codes to retry
    retryable_errors=['rate_limited']  # Error types to retry
)

client = RetryClient(config)
```

### Handling Errors

```python
from mega_defi.core.retry_client import RetryClient, RetryError

client = RetryClient()

try:
    result = client.execute_with_retry(lambda: copilot_api_call())
except RetryError as e:
    print(f"Failed after {e.attempts} attempts")
    print(f"Last error: {e.last_error}")
except Exception as e:
    # Non-retryable error
    print(f"Fatal error: {e}")
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `maxRetries` | number | 5 | Maximum number of retry attempts |
| `baseDelayMs` | number | 1000 | Initial delay between retries (ms) |
| `maxDelayMs` | number | 32000 | Maximum delay cap (ms) |
| `backoffMultiplier` | number | 2.0 | Exponential backoff multiplier |
| `retryableStatusCodes` | number[] | [408, 429, 500, 502, 503, 504] | HTTP status codes that trigger retry |
| `retryableErrors` | string[] | See below | Error codes that trigger retry |

**Default retryable errors:**
- `ECONNRESET` / `ConnectionResetError` - Connection reset
- `ETIMEDOUT` / `TimeoutError` - Request timeout
- `rate_limited` - Rate limit errors
- `too_many_requests` - Too many requests errors

## Exponential Backoff Behavior

The retry client uses exponential backoff with jitter:

```
Delay = min(baseDelay × (multiplier ^ attempt) ± jitter, maxDelay)
```

Example with default settings:
- Attempt 1: ~1000ms (1s)
- Attempt 2: ~2000ms (2s)
- Attempt 3: ~4000ms (4s)
- Attempt 4: ~8000ms (8s)
- Attempt 5: ~16000ms (16s)

Jitter adds ±20% randomization to prevent multiple clients from retrying simultaneously.

## Best Practices

### 1. Choose Appropriate Retry Counts

```typescript
// For critical operations that must succeed
const criticalClient = new RetryClient({ maxRetries: 10 });

// For non-critical operations
const optionalClient = new RetryClient({ maxRetries: 3 });
```

### 2. Set Reasonable Timeouts

```typescript
const client = new RetryClient({
  maxRetries: 5,
  baseDelayMs: 2000,  // Start with 2s
  maxDelayMs: 60000   // Cap at 1 minute
});
```

### 3. Handle Specific Error Types

```typescript
const client = new RetryClient({
  retryableStatusCodes: [429],  // Only retry rate limits
  retryableErrors: ['rate_limited', 'too_many_requests']
});
```

### 4. Use Different Clients for Different APIs

```typescript
// For APIs with strict rate limits
const strictClient = new RetryClient({
  maxRetries: 10,
  baseDelayMs: 5000,
  backoffMultiplier: 3
});

// For faster APIs
const fastClient = new RetryClient({
  maxRetries: 3,
  baseDelayMs: 500,
  backoffMultiplier: 2
});
```

### 5. Log Retry Attempts

The retry client automatically logs retry attempts with warnings. You can also add custom logging:

```typescript
const client = new RetryClient();

try {
  const result = await client.executeWithRetry(async () => {
    console.log('Attempting API call...');
    return await apiCall();
  });
  console.log('Success!');
} catch (error) {
  console.error('All retries failed:', error);
}
```

## GitHub Actions Setup

If you're using this with GitHub Actions and Copilot:

### 1. Configure Action Steps

Follow the setup steps at: https://gh.io/copilot/actions-setup-steps

### 2. Add Firewall Rules

Add Copilot API URLs to your firewall allow list:
- See: https://gh.io/copilot/firewall-config

### 3. Check Token Allocation

Ensure your GitHub account has sufficient Copilot tokens for your workflow volume.

### 4. Use Retry Client in Workflows

```typescript
import { RetryClient } from './src/core/retryClient';

const client = new RetryClient({
  maxRetries: 5,
  baseDelayMs: 2000,
  backoffMultiplier: 2
});

// Use in your GitHub Actions scripts
const result = await client.executeWithRetry(async () => {
  return await callCopilotApi();
});
```

## Common Use Cases

### Rate-Limited APIs

```typescript
const rateLimitClient = new RetryClient({
  maxRetries: 10,
  baseDelayMs: 5000,
  retryableStatusCodes: [429],
  retryableErrors: ['rate_limited']
});
```

### Unreliable Network

```typescript
const networkClient = new RetryClient({
  maxRetries: 5,
  baseDelayMs: 1000,
  retryableStatusCodes: [408, 502, 503, 504],
  retryableErrors: ['ECONNRESET', 'ETIMEDOUT']
});
```

### Critical Operations

```typescript
const criticalClient = new RetryClient({
  maxRetries: 10,
  baseDelayMs: 2000,
  maxDelayMs: 60000,
  backoffMultiplier: 2
});
```

## Testing

See the test files for comprehensive examples:
- TypeScript: `tests/test_retry_client.ts`
- Python: `tests/test_retry_client.py`

## Troubleshooting

### Still Getting Rate Limited?

1. Increase `baseDelayMs` and `maxRetries`
2. Check your API token allocation
3. Add the API to your firewall allow list
4. Verify your API key is valid

### Retries Taking Too Long?

1. Reduce `maxRetries`
2. Reduce `maxDelayMs`
3. Adjust `backoffMultiplier` to grow slower

### Not Retrying Expected Errors?

1. Check the error type/status code
2. Add custom error types to `retryableErrors`
3. Add custom status codes to `retryableStatusCodes`

## Additional Resources

- [GitHub Copilot Actions Setup](https://gh.io/copilot/actions-setup-steps)
- [Firewall Configuration](https://gh.io/copilot/firewall-config)
- [Exponential Backoff Algorithm](https://en.wikipedia.org/wiki/Exponential_backoff)
