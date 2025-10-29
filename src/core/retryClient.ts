/**
 * Retry Client with Exponential Backoff
 * 
 * Provides a robust API client with automatic retry logic and exponential backoff
 * for handling rate limits and transient failures.
 */

export interface RetryConfig {
    maxRetries?: number;
    baseDelayMs?: number;
    maxDelayMs?: number;
    backoffMultiplier?: number;
    retryableStatusCodes?: number[];
    retryableErrors?: string[];
}

export interface RetryContext {
    attempt: number;
    maxRetries: number;
    lastError?: Error;
    nextDelayMs: number;
}

export class RetryError extends Error {
    constructor(
        message: string,
        public readonly attempts: number,
        public readonly lastError?: Error
    ) {
        super(message);
        this.name = 'RetryError';
    }
}

export class RetryClient {
    private config: Required<RetryConfig>;

    constructor(config: RetryConfig = {}) {
        this.config = {
            maxRetries: config.maxRetries ?? 5,
            baseDelayMs: config.baseDelayMs ?? 1000,
            maxDelayMs: config.maxDelayMs ?? 32000,
            backoffMultiplier: config.backoffMultiplier ?? 2,
            retryableStatusCodes: config.retryableStatusCodes ?? [408, 429, 500, 502, 503, 504],
            retryableErrors: config.retryableErrors ?? [
                'ECONNRESET',
                'ETIMEDOUT',
                'ENOTFOUND',
                'ENETUNREACH',
                'rate_limited',
                'too_many_requests'
            ]
        };
    }

    /**
     * Execute a function with retry logic and exponential backoff
     */
    async executeWithRetry<T>(
        fn: () => Promise<T>,
        context?: Partial<RetryConfig>
    ): Promise<T> {
        const config = { ...this.config, ...context };
        let lastError: Error | undefined;

        for (let attempt = 0; attempt < config.maxRetries; attempt++) {
            try {
                return await fn();
            } catch (error) {
                lastError = error as Error;
                
                // Check if we should retry
                if (!this.shouldRetry(error, attempt, config)) {
                    throw error;
                }

                // Calculate delay with exponential backoff
                const delayMs = this.calculateDelay(attempt, config);

                console.warn(
                    `Retry attempt ${attempt + 1}/${config.maxRetries} after ${delayMs}ms. ` +
                    `Error: ${(error as Error).message}`
                );

                // Wait before retrying
                await this.sleep(delayMs);
            }
        }

        // All retries exhausted
        throw new RetryError(
            `Failed after ${config.maxRetries} retries`,
            config.maxRetries,
            lastError
        );
    }

    /**
     * Execute an HTTP request with retry logic
     */
    async fetchWithRetry(
        url: string,
        options?: RequestInit,
        retryConfig?: Partial<RetryConfig>
    ): Promise<Response> {
        return this.executeWithRetry(async () => {
            const response = await fetch(url, options);
            
            // Check if response status is retryable
            if (!response.ok && this.isRetryableStatusCode(response.status)) {
                const error = new Error(`HTTP ${response.status}: ${response.statusText}`) as any;
                error.status = response.status;
                error.response = response;
                throw error;
            }

            return response;
        }, retryConfig);
    }

    /**
     * Determine if an error should trigger a retry
     */
    private shouldRetry(
        error: unknown,
        attempt: number,
        config: Required<RetryConfig>
    ): boolean {
        // Don't retry if we've exceeded max retries
        if (attempt >= config.maxRetries - 1) {
            return false;
        }

        const err = error as any;

        // Check for retryable HTTP status codes
        if (err.status && this.isRetryableStatusCode(err.status, config)) {
            return true;
        }

        // Check for retryable error codes
        if (err.code && config.retryableErrors.includes(err.code)) {
            return true;
        }

        // Check error message for rate limiting
        const errorMessage = err.message?.toLowerCase() || '';
        if (
            errorMessage.includes('rate limit') ||
            errorMessage.includes('too many requests') ||
            errorMessage.includes('throttled')
        ) {
            return true;
        }

        // Don't retry by default
        return false;
    }

    /**
     * Check if HTTP status code is retryable
     */
    private isRetryableStatusCode(
        statusCode: number,
        config?: Required<RetryConfig>
    ): boolean {
        const codes = config?.retryableStatusCodes ?? this.config.retryableStatusCodes;
        return codes.includes(statusCode);
    }

    /**
     * Calculate delay with exponential backoff
     */
    private calculateDelay(
        attempt: number,
        config: Required<RetryConfig>
    ): number {
        // Exponential backoff: baseDelay * (multiplier ^ attempt)
        const exponentialDelay = config.baseDelayMs * Math.pow(config.backoffMultiplier, attempt);
        
        // Add jitter to prevent thundering herd (±20% randomization)
        const jitter = exponentialDelay * 0.2 * (Math.random() - 0.5);
        
        // Cap at maximum delay
        return Math.min(exponentialDelay + jitter, config.maxDelayMs);
    }

    /**
     * Sleep for specified milliseconds
     */
    private sleep(ms: number): Promise<void> {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Get current configuration
     */
    getConfig(): Required<RetryConfig> {
        return { ...this.config };
    }

    /**
     * Update configuration
     */
    updateConfig(config: Partial<RetryConfig>): void {
        this.config = { ...this.config, ...config };
    }
}

/**
 * Create a default retry client instance
 */
export const defaultRetryClient = new RetryClient();

/**
 * Convenience function for executing with retry
 */
export async function withRetry<T>(
    fn: () => Promise<T>,
    config?: RetryConfig
): Promise<T> {
    const client = new RetryClient(config);
    return client.executeWithRetry(fn);
}
