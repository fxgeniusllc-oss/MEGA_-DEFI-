/**
 * Example: Using Retry Client for API Calls with Exponential Backoff
 * 
 * This example demonstrates how to use the retry client to handle
 * rate-limited API calls with automatic retry and exponential backoff.
 */

import { RetryClient, RetryConfig, RetryError, withRetry } from '../src/core/retryClient.js';

async function exampleBasicRetry(): Promise<void> {
    console.log('='.repeat(60));
    console.log('Example 1: Basic Retry');
    console.log('='.repeat(60));

    let attemptCount = 0;

    const flakyOperation = async (): Promise<string> => {
        attemptCount++;
        console.log(`  Attempt ${attemptCount}`);

        if (attemptCount < 3) {
            throw new Error('Temporary failure');
        }

        return 'Success!';
    };

    try {
        const result = await withRetry(flakyOperation, { maxRetries: 5 });
        console.log(`✓ Result: ${result}`);
    } catch (error) {
        if (error instanceof RetryError) {
            console.log(`✗ Failed after ${error.attempts} attempts: ${error.lastError?.message}`);
        }
    }

    console.log();
}

async function exampleRateLimitedAPI(): Promise<void> {
    console.log('='.repeat(60));
    console.log('Example 2: Rate-Limited API');
    console.log('='.repeat(60));

    let callCount = 0;

    const rateLimitedAPI = async (): Promise<{ data: string }> => {
        callCount++;
        console.log(`  API Call ${callCount}`);

        if (callCount < 4) {
            const error: any = new Error('Rate limit exceeded');
            error.status = 429;
            throw error;
        }

        return { data: 'API Response' };
    };

    const client = new RetryClient({
        maxRetries: 10,
        baseDelayMs: 1000,
        backoffMultiplier: 2,
        retryableStatusCodes: [429]
    });

    try {
        const startTime = Date.now();
        const result = await client.executeWithRetry(rateLimitedAPI);
        const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
        console.log(`✓ Success after ${elapsed}s: ${JSON.stringify(result)}`);
    } catch (error) {
        console.log(`✗ Failed: ${error}`);
    }

    console.log();
}

async function exampleCustomConfiguration(): Promise<void> {
    console.log('='.repeat(60));
    console.log('Example 3: Custom Configuration');
    console.log('='.repeat(60));

    const config: RetryConfig = {
        maxRetries: 5,
        baseDelayMs: 500,
        maxDelayMs: 10000,
        backoffMultiplier: 3
    };

    const client = new RetryClient(config);

    let attempts = 0;

    const operation = async (): Promise<string> => {
        attempts++;
        if (attempts < 3) {
            const error: any = new Error('Network issue');
            error.code = 'ECONNRESET';
            throw error;
        }
        return 'Connected';
    };

    try {
        const result = await client.executeWithRetry(operation);
        console.log(`✓ Result: ${result}`);
        console.log(`  Total attempts: ${attempts}`);
    } catch (error) {
        console.log(`✗ Failed: ${error}`);
    }

    console.log();
}

async function exampleHTTPFetch(): Promise<void> {
    console.log('='.repeat(60));
    console.log('Example 4: HTTP Fetch (Simulated)');
    console.log('='.repeat(60));

    // Simulated fetch that fails first 2 times with rate limit
    let callCount = 0;
    
    const mockFetch = async (url: string, options?: RequestInit): Promise<Response> => {
        callCount++;
        console.log(`  HTTP Request ${callCount}`);

        if (callCount < 3) {
            return {
                ok: false,
                status: 429,
                statusText: 'Too Many Requests'
            } as Response;
        }

        return {
            ok: true,
            status: 200,
            statusText: 'OK',
            json: async () => ({ data: 'Success' })
        } as Response;
    };

    // Override global fetch temporarily
    const originalFetch = global.fetch;
    (global as any).fetch = mockFetch;

    const client = new RetryClient({
        maxRetries: 5,
        baseDelayMs: 500
    });

    try {
        const response = await client.fetchWithRetry(
            'https://api.example.com/data',
            {
                method: 'GET',
                headers: { 'Authorization': 'Bearer token' }
            }
        );
        console.log(`✓ HTTP ${response.status}: Success`);
    } catch (error) {
        console.log(`✗ Failed: ${error}`);
    } finally {
        // Restore original fetch
        global.fetch = originalFetch;
    }

    console.log();
}

async function exampleErrorHandling(): Promise<void> {
    console.log('='.repeat(60));
    console.log('Example 5: Error Handling');
    console.log('='.repeat(60));

    const nonRetryableError = async (): Promise<void> => {
        throw new TypeError('Invalid input - should not retry');
    };

    const retryableError = async (): Promise<void> => {
        const error: any = new Error('Service unavailable');
        error.status = 503;
        throw error;
    };

    const client = new RetryClient({ maxRetries: 3 });

    // Non-retryable error
    console.log('  Testing non-retryable error...');
    try {
        await client.executeWithRetry(nonRetryableError);
    } catch (error) {
        if (error instanceof TypeError) {
            console.log(`  ✓ Correctly failed immediately: ${error.message}`);
        } else if (error instanceof RetryError) {
            console.log(`  ✗ Should not have retried`);
        }
    }

    // Retryable error
    console.log('\n  Testing retryable error...');
    try {
        await client.executeWithRetry(retryableError);
    } catch (error) {
        if (error instanceof RetryError) {
            console.log(`  ✓ Correctly retried ${error.attempts} times before failing`);
        }
    }

    console.log();
}

async function exampleCopilotAPI(): Promise<void> {
    console.log('='.repeat(60));
    console.log('Example 6: Copilot API Integration');
    console.log('='.repeat(60));

    console.log('Configuration for Copilot API:');

    const config: RetryConfig = {
        maxRetries: 10,
        baseDelayMs: 2000,
        maxDelayMs: 60000,
        backoffMultiplier: 2,
        retryableStatusCodes: [408, 429, 500, 502, 503, 504],
        retryableErrors: ['rate_limited', 'too_many_requests']
    };

    console.log(`  Max Retries: ${config.maxRetries}`);
    console.log(`  Base Delay: ${config.baseDelayMs}ms`);
    console.log(`  Max Delay: ${config.maxDelayMs}ms`);
    console.log(`  Backoff Multiplier: ${config.backoffMultiplier}`);
    console.log(`  Retryable Status Codes: ${config.retryableStatusCodes?.join(', ')}`);
    console.log(`  Retryable Errors: ${config.retryableErrors?.join(', ')}`);

    console.log('\nExpected delay progression:');
    const client = new RetryClient(config);
    for (let i = 0; i < 5; i++) {
        const delay = (client as any).calculateDelay(i, client.getConfig());
        console.log(`  Attempt ${i + 1}: ~${delay.toFixed(0)}ms`);
    }

    console.log('\n✓ Use this configuration for Copilot API calls');
    console.log();
}

async function main(): Promise<void> {
    console.log('\n');
    console.log('╔' + '═'.repeat(58) + '╗');
    console.log('║' + ' '.repeat(10) + 'RETRY CLIENT EXAMPLES' + ' '.repeat(27) + '║');
    console.log('╚' + '═'.repeat(58) + '╝');
    console.log();

    await exampleBasicRetry();
    await exampleRateLimitedAPI();
    await exampleCustomConfiguration();
    await exampleHTTPFetch();
    await exampleErrorHandling();
    await exampleCopilotAPI();

    console.log('='.repeat(60));
    console.log('All examples completed!');
    console.log('='.repeat(60));
    console.log();
    console.log('See RETRY_BACKOFF_GUIDE.md for detailed usage documentation');
    console.log();
}

// Run if executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
    main().catch(console.error);
}

export {
    exampleBasicRetry,
    exampleRateLimitedAPI,
    exampleCustomConfiguration,
    exampleHTTPFetch,
    exampleErrorHandling,
    exampleCopilotAPI
};
