/**
 * Configuration Module - Environment Variable Management for TypeScript
 * =====================================================================
 * 
 * Loads and manages environment variables from .env file for TypeScript modules.
 */

import { existsSync, readFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

// Get the directory of this module
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

/**
 * Find .env file in project root
 */
function findDotenv(): string | null {
    const root = resolve(__dirname, '../..');
    const envFile = resolve(root, '.env');
    
    if (existsSync(envFile)) {
        return envFile;
    }
    return null;
}

/**
 * Load environment variables from .env file
 */
function loadDotenv(): void {
    const envFile = findDotenv();
    
    if (envFile) {
        try {
            const content = readFileSync(envFile, 'utf-8');
            const lines = content.split('\n');
            
            for (const line of lines) {
                const trimmed = line.trim();
                
                // Skip comments and empty lines
                if (!trimmed || trimmed.startsWith('#')) {
                    continue;
                }
                
                // Parse KEY=VALUE
                const equalIndex = trimmed.indexOf('=');
                if (equalIndex > 0) {
                    let key = trimmed.substring(0, equalIndex).trim();
                    let value = trimmed.substring(equalIndex + 1).trim();
                    
                    // Remove quotes if present
                    if ((value.startsWith('"') && value.endsWith('"')) ||
                        (value.startsWith("'") && value.endsWith("'"))) {
                        value = value.slice(1, -1);
                    }
                    
                    // Only set if not already in environment
                    if (!process.env[key]) {
                        process.env[key] = value;
                    }
                }
            }
            
            console.log(`Loaded environment variables from ${envFile}`);
        } catch (error) {
            console.warn(`Failed to load .env file: ${error}`);
        }
    } else {
        console.log('No .env file found, using system environment variables');
    }
}

// Load environment variables on module import
loadDotenv();

/**
 * Configuration class to access environment variables with defaults
 */
export class Config {
    // ============================================
    // Network Configuration
    // ============================================
    
    static getEthereumRpcUrl(): string {
        return process.env.ETHEREUM_RPC_URL || 'https://eth-mainnet.g.alchemy.com/v2/demo';
    }
    
    static getEthereumChainId(): number {
        return parseInt(process.env.ETHEREUM_CHAIN_ID || '1', 10);
    }
    
    static getEthereumWebsocketUrl(): string {
        return process.env.ETHEREUM_WEBSOCKET_URL || '';
    }
    
    static getBscRpcUrl(): string {
        return process.env.BSC_RPC_URL || 'https://bsc-dataseed.binance.org/';
    }
    
    static getPolygonRpcUrl(): string {
        return process.env.POLYGON_RPC_URL || 'https://polygon-rpc.com';
    }
    
    static getArbitrumRpcUrl(): string {
        return process.env.ARBITRUM_RPC_URL || 'https://arb1.arbitrum.io/rpc';
    }
    
    static getOptimismRpcUrl(): string {
        return process.env.OPTIMISM_RPC_URL || 'https://mainnet.optimism.io';
    }
    
    // ============================================
    // API Keys and Credentials
    // ============================================
    
    static getAlchemyApiKey(): string {
        return process.env.ALCHEMY_API_KEY || '';
    }
    
    static getInfuraApiKey(): string {
        return process.env.INFURA_API_KEY || '';
    }
    
    static getEtherscanApiKey(): string {
        return process.env.ETHERSCAN_API_KEY || '';
    }
    
    static getCoingeckoApiKey(): string {
        return process.env.COINGECKO_API_KEY || '';
    }
    
    static getTheGraphApiKey(): string {
        return process.env.THEGRAPH_API_KEY || '';
    }
    
    // ============================================
    // Trading Account Configuration
    // ============================================
    
    static getPrivateKey(): string {
        return process.env.PRIVATE_KEY || '';
    }
    
    static getWalletAddress(): string {
        return process.env.WALLET_ADDRESS || '';
    }
    
    // ============================================
    // DEX Configuration
    // ============================================
    
    static getUniswapV2Router(): string {
        return process.env.UNISWAP_V2_ROUTER || '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D';
    }
    
    static getUniswapV3Router(): string {
        return process.env.UNISWAP_V3_ROUTER || '0xE592427A0AEce92De3Edee1F18E0157C05861564';
    }
    
    static getSushiswapRouter(): string {
        return process.env.SUSHISWAP_ROUTER || '0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F';
    }
    
    static getOneInchApiUrl(): string {
        return process.env.ONEINCH_API_URL || 'https://api.1inch.io/v5.0';
    }
    
    static getOneInchApiKey(): string {
        return process.env.ONEINCH_API_KEY || '';
    }
    
    // ============================================
    // Risk Management
    // ============================================
    
    static getInitialPortfolioValue(): number {
        return parseFloat(process.env.INITIAL_PORTFOLIO_VALUE || '10000');
    }
    
    static getMaxPortfolioExposure(): number {
        return parseFloat(process.env.MAX_PORTFOLIO_EXPOSURE || '0.80');
    }
    
    static getMaxPositionSize(): number {
        return parseFloat(process.env.MAX_POSITION_SIZE || '0.20');
    }
    
    static getMaxRiskPerTrade(): number {
        return parseFloat(process.env.MAX_RISK_PER_TRADE || '0.02');
    }
    
    static getMinRiskRewardRatio(): number {
        return parseFloat(process.env.MIN_RISK_REWARD_RATIO || '2.0');
    }
    
    static getDefaultStopLossPct(): number {
        return parseFloat(process.env.DEFAULT_STOP_LOSS_PCT || '0.10');
    }
    
    static getDefaultTakeProfitPct(): number {
        return parseFloat(process.env.DEFAULT_TAKE_PROFIT_PCT || '0.25');
    }
    
    // ============================================
    // Strategy Configuration
    // ============================================
    
    static getArbitrageMinProfit(): number {
        return parseFloat(process.env.ARBITRAGE_MIN_PROFIT || '0.005');
    }
    
    static getArbitrageMaxGasCost(): number {
        return parseFloat(process.env.ARBITRAGE_MAX_GAS_COST || '500');
    }
    
    static getFlashLoanMinProfit(): number {
        return parseFloat(process.env.FLASH_LOAN_MIN_PROFIT || '0.005');
    }
    
    static getMevMinTransactionSize(): number {
        return parseFloat(process.env.MEV_MIN_TRANSACTION_SIZE || '10000');
    }
    
    static getMevMinExpectedProfit(): number {
        return parseFloat(process.env.MEV_MIN_EXPECTED_PROFIT || '0.01');
    }
    
    // ============================================
    // Gas Configuration
    // ============================================
    
    static getMaxGasPriceGwei(): number {
        return parseFloat(process.env.MAX_GAS_PRICE_GWEI || '300');
    }
    
    static getTargetGasPriceGwei(): number {
        return parseFloat(process.env.TARGET_GAS_PRICE_GWEI || '50');
    }
    
    static getMinGasPriceGwei(): number {
        return parseFloat(process.env.MIN_GAS_PRICE_GWEI || '10');
    }
    
    static getDefaultGasLimit(): number {
        return parseInt(process.env.DEFAULT_GAS_LIMIT || '500000', 10);
    }
    
    static getUseDynamicGas(): boolean {
        return (process.env.USE_DYNAMIC_GAS || 'true').toLowerCase() === 'true';
    }
    
    // ============================================
    // Execution Configuration
    // ============================================
    
    static getConfirmationBlocks(): number {
        return parseInt(process.env.CONFIRMATION_BLOCKS || '2', 10);
    }
    
    static getTxTimeoutSeconds(): number {
        return parseInt(process.env.TX_TIMEOUT_SECONDS || '300', 10);
    }
    
    static getMaxSlippage(): number {
        return parseFloat(process.env.MAX_SLIPPAGE || '0.005');
    }
    
    static getUseFlashbots(): boolean {
        return (process.env.USE_FLASHBOTS || 'true').toLowerCase() === 'true';
    }
    
    static getFlashbotsRpc(): string {
        return process.env.FLASHBOTS_RPC || 'https://rpc.flashbots.net';
    }
    
    // ============================================
    // Monitoring & Alerts
    // ============================================
    
    static getTelegramBotToken(): string {
        return process.env.TELEGRAM_BOT_TOKEN || '';
    }
    
    static getTelegramChatId(): string {
        return process.env.TELEGRAM_CHAT_ID || '';
    }
    
    static getEnableTelegramAlerts(): boolean {
        return (process.env.ENABLE_TELEGRAM_ALERTS || 'false').toLowerCase() === 'true';
    }
    
    static getDiscordWebhookUrl(): string {
        return process.env.DISCORD_WEBHOOK_URL || '';
    }
    
    // ============================================
    // Logging & Telemetry
    // ============================================
    
    static getLogLevel(): string {
        return process.env.LOG_LEVEL || 'INFO';
    }
    
    static getLogFile(): string {
        return process.env.LOG_FILE || 'logs/mega_defi.log';
    }
    
    static getEnableMetrics(): boolean {
        return (process.env.ENABLE_METRICS || 'true').toLowerCase() === 'true';
    }
    
    // ============================================
    // Development & Testing
    // ============================================
    
    static getEnvironment(): string {
        return process.env.ENVIRONMENT || 'production';
    }
    
    static getDebugMode(): boolean {
        return (process.env.DEBUG_MODE || 'false').toLowerCase() === 'true';
    }
    
    static getDryRun(): boolean {
        return (process.env.DRY_RUN || 'false').toLowerCase() === 'true';
    }
    
    static getTestMode(): boolean {
        return (process.env.TEST_MODE || 'false').toLowerCase() === 'true';
    }
    
    // ============================================
    // Utility Methods
    // ============================================
    
    static getAllRpcUrls(): Record<string, string> {
        return {
            ethereum: Config.getEthereumRpcUrl(),
            bsc: Config.getBscRpcUrl(),
            polygon: Config.getPolygonRpcUrl(),
            arbitrum: Config.getArbitrumRpcUrl(),
            optimism: Config.getOptimismRpcUrl(),
        };
    }
    
    static getRiskParams(): Record<string, number> {
        return {
            maxPortfolioExposure: Config.getMaxPortfolioExposure(),
            maxPositionSize: Config.getMaxPositionSize(),
            maxRiskPerTrade: Config.getMaxRiskPerTrade(),
            minRiskRewardRatio: Config.getMinRiskRewardRatio(),
            defaultStopLossPct: Config.getDefaultStopLossPct(),
            defaultTakeProfitPct: Config.getDefaultTakeProfitPct(),
        };
    }
    
    static isProduction(): boolean {
        return Config.getEnvironment().toLowerCase() === 'production';
    }
    
    static validateConfig(): { valid: boolean; issues: string[]; warnings: string[] } {
        const issues: string[] = [];
        const warnings: string[] = [];
        
        // Check critical settings
        if (!Config.getEthereumRpcUrl()) {
            warnings.push('No Ethereum RPC URL configured');
        }
        
        if (!Config.getPrivateKey() && !Config.getTestMode()) {
            warnings.push('No private key configured (required for live trading)');
        }
        
        if (!Config.getWalletAddress() && !Config.getTestMode()) {
            warnings.push('No wallet address configured');
        }
        
        // Check risk parameters
        if (Config.getMaxPositionSize() > 0.5) {
            warnings.push('Max position size is very high (>50%)');
        }
        
        if (Config.getMaxRiskPerTrade() > 0.1) {
            warnings.push('Max risk per trade is very high (>10%)');
        }
        
        return {
            valid: issues.length === 0,
            issues,
            warnings,
        };
    }
}

// Default export for convenience
export default Config;
