"""
Configuration Module - Environment Variable Management
======================================================

Loads and manages environment variables from .env file for all modules.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Find the .env file in the project root
def find_dotenv() -> Optional[Path]:
    """Find .env file starting from current directory and going up."""
    current = Path(__file__).resolve().parent
    root = current.parent  # Go up to project root
    env_file = root / '.env'
    
    if env_file.exists():
        return env_file
    return None


def load_dotenv():
    """Load environment variables from .env file if it exists."""
    env_file = find_dotenv()
    
    if env_file:
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse KEY=VALUE
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        
                        # Only set if not already in environment
                        if key not in os.environ:
                            os.environ[key] = value
            
            logger.info(f"Loaded environment variables from {env_file}")
        except Exception as e:
            logger.warning(f"Failed to load .env file: {e}")
    else:
        logger.info("No .env file found, using system environment variables")


# Load environment variables on module import
load_dotenv()


class Config:
    """Configuration class to access environment variables with defaults."""
    
    # ============================================
    # Network Configuration
    # ============================================
    
    @staticmethod
    def get_ethereum_rpc_url() -> str:
        return os.getenv('ETHEREUM_RPC_URL', 'https://eth-mainnet.g.alchemy.com/v2/demo')
    
    @staticmethod
    def get_ethereum_chain_id() -> int:
        return int(os.getenv('ETHEREUM_CHAIN_ID', '1'))
    
    @staticmethod
    def get_ethereum_websocket_url() -> str:
        return os.getenv('ETHEREUM_WEBSOCKET_URL', '')
    
    @staticmethod
    def get_bsc_rpc_url() -> str:
        return os.getenv('BSC_RPC_URL', 'https://bsc-dataseed.binance.org/')
    
    @staticmethod
    def get_bsc_chain_id() -> int:
        return int(os.getenv('BSC_CHAIN_ID', '56'))
    
    @staticmethod
    def get_polygon_rpc_url() -> str:
        return os.getenv('POLYGON_RPC_URL', 'https://polygon-rpc.com')
    
    @staticmethod
    def get_polygon_chain_id() -> int:
        return int(os.getenv('POLYGON_CHAIN_ID', '137'))
    
    @staticmethod
    def get_arbitrum_rpc_url() -> str:
        return os.getenv('ARBITRUM_RPC_URL', 'https://arb1.arbitrum.io/rpc')
    
    @staticmethod
    def get_arbitrum_chain_id() -> int:
        return int(os.getenv('ARBITRUM_CHAIN_ID', '42161'))
    
    @staticmethod
    def get_optimism_rpc_url() -> str:
        return os.getenv('OPTIMISM_RPC_URL', 'https://mainnet.optimism.io')
    
    @staticmethod
    def get_optimism_chain_id() -> int:
        return int(os.getenv('OPTIMISM_CHAIN_ID', '10'))
    
    # ============================================
    # API Keys and Credentials
    # ============================================
    
    @staticmethod
    def get_alchemy_api_key() -> str:
        return os.getenv('ALCHEMY_API_KEY', '')
    
    @staticmethod
    def get_infura_api_key() -> str:
        return os.getenv('INFURA_API_KEY', '')
    
    @staticmethod
    def get_etherscan_api_key() -> str:
        return os.getenv('ETHERSCAN_API_KEY', '')
    
    @staticmethod
    def get_coingecko_api_key() -> str:
        return os.getenv('COINGECKO_API_KEY', '')
    
    @staticmethod
    def get_coinmarketcap_api_key() -> str:
        return os.getenv('COINMARKETCAP_API_KEY', '')
    
    @staticmethod
    def get_thegraph_api_key() -> str:
        return os.getenv('THEGRAPH_API_KEY', '')
    
    # ============================================
    # Trading Account Configuration
    # ============================================
    
    @staticmethod
    def get_private_key() -> str:
        return os.getenv('PRIVATE_KEY', '')
    
    @staticmethod
    def get_wallet_address() -> str:
        return os.getenv('WALLET_ADDRESS', '')
    
    @staticmethod
    def get_treasury_address() -> str:
        return os.getenv('TREASURY_ADDRESS', '')
    
    # ============================================
    # DEX Configuration
    # ============================================
    
    @staticmethod
    def get_uniswap_v2_router() -> str:
        return os.getenv('UNISWAP_V2_ROUTER', '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D')
    
    @staticmethod
    def get_uniswap_v3_router() -> str:
        return os.getenv('UNISWAP_V3_ROUTER', '0xE592427A0AEce92De3Edee1F18E0157C05861564')
    
    @staticmethod
    def get_sushiswap_router() -> str:
        return os.getenv('SUSHISWAP_ROUTER', '0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F')
    
    @staticmethod
    def get_pancakeswap_router() -> str:
        return os.getenv('PANCAKESWAP_ROUTER', '0x10ED43C718714eb63d5aA57B78B54704E256024E')
    
    @staticmethod
    def get_oneinch_api_url() -> str:
        return os.getenv('ONEINCH_API_URL', 'https://api.1inch.io/v5.0')
    
    @staticmethod
    def get_oneinch_api_key() -> str:
        return os.getenv('ONEINCH_API_KEY', '')
    
    # ============================================
    # Lending Protocol Configuration
    # ============================================
    
    @staticmethod
    def get_aave_lending_pool() -> str:
        return os.getenv('AAVE_LENDING_POOL', '0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9')
    
    @staticmethod
    def get_compound_comptroller() -> str:
        return os.getenv('COMPOUND_COMPTROLLER', '0x3d9819210A31b4961b30EF54bE2aeD79B9c9Cd3B')
    
    # ============================================
    # Flash Loan Providers
    # ============================================
    
    @staticmethod
    def get_aave_flash_loan_pool() -> str:
        return os.getenv('AAVE_FLASH_LOAN_POOL', '0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9')
    
    @staticmethod
    def get_dydx_solo_margin() -> str:
        return os.getenv('DYDX_SOLO_MARGIN', '0x1E0447b19BB6EcFdAe1e4AE1694b0C3659614e4e')
    
    # ============================================
    # Risk Management
    # ============================================
    
    @staticmethod
    def get_initial_portfolio_value() -> float:
        return float(os.getenv('INITIAL_PORTFOLIO_VALUE', '10000'))
    
    @staticmethod
    def get_max_portfolio_exposure() -> float:
        return float(os.getenv('MAX_PORTFOLIO_EXPOSURE', '0.80'))
    
    @staticmethod
    def get_max_position_size() -> float:
        return float(os.getenv('MAX_POSITION_SIZE', '0.20'))
    
    @staticmethod
    def get_min_position_size() -> float:
        return float(os.getenv('MIN_POSITION_SIZE', '0.01'))
    
    @staticmethod
    def get_max_risk_per_trade() -> float:
        return float(os.getenv('MAX_RISK_PER_TRADE', '0.02'))
    
    @staticmethod
    def get_min_risk_reward_ratio() -> float:
        return float(os.getenv('MIN_RISK_REWARD_RATIO', '2.0'))
    
    @staticmethod
    def get_max_daily_loss() -> float:
        return float(os.getenv('MAX_DAILY_LOSS', '0.05'))
    
    @staticmethod
    def get_default_stop_loss_pct() -> float:
        return float(os.getenv('DEFAULT_STOP_LOSS_PCT', '0.10'))
    
    @staticmethod
    def get_default_take_profit_pct() -> float:
        return float(os.getenv('DEFAULT_TAKE_PROFIT_PCT', '0.25'))
    
    # ============================================
    # Strategy Configuration
    # ============================================
    
    @staticmethod
    def get_arbitrage_min_profit() -> float:
        return float(os.getenv('ARBITRAGE_MIN_PROFIT', '0.005'))
    
    @staticmethod
    def get_arbitrage_max_gas_cost() -> float:
        return float(os.getenv('ARBITRAGE_MAX_GAS_COST', '500'))
    
    @staticmethod
    def get_arbitrage_min_liquidity() -> float:
        return float(os.getenv('ARBITRAGE_MIN_LIQUIDITY', '10000'))
    
    @staticmethod
    def get_flash_loan_min_profit() -> float:
        return float(os.getenv('FLASH_LOAN_MIN_PROFIT', '0.005'))
    
    @staticmethod
    def get_cross_chain_min_profit() -> float:
        return float(os.getenv('CROSS_CHAIN_MIN_PROFIT', '0.03'))
    
    @staticmethod
    def get_cross_chain_max_bridge_time() -> int:
        return int(os.getenv('CROSS_CHAIN_MAX_BRIDGE_TIME', '600'))
    
    @staticmethod
    def get_liquidation_min_health_factor() -> float:
        return float(os.getenv('LIQUIDATION_MIN_HEALTH_FACTOR', '1.05'))
    
    @staticmethod
    def get_liquidation_min_profit() -> float:
        return float(os.getenv('LIQUIDATION_MIN_PROFIT', '0.02'))
    
    @staticmethod
    def get_mev_min_transaction_size() -> float:
        return float(os.getenv('MEV_MIN_TRANSACTION_SIZE', '10000'))
    
    @staticmethod
    def get_mev_min_expected_profit() -> float:
        return float(os.getenv('MEV_MIN_EXPECTED_PROFIT', '0.01'))
    
    @staticmethod
    def get_yield_min_apy() -> float:
        return float(os.getenv('YIELD_MIN_APY', '0.15'))
    
    @staticmethod
    def get_yield_max_protocol_risk() -> float:
        return float(os.getenv('YIELD_MAX_PROTOCOL_RISK', '0.50'))
    
    @staticmethod
    def get_stat_arb_z_score_threshold() -> float:
        return float(os.getenv('STAT_ARB_Z_SCORE_THRESHOLD', '2.0'))
    
    @staticmethod
    def get_stat_arb_correlation_threshold() -> float:
        return float(os.getenv('STAT_ARB_CORRELATION_THRESHOLD', '0.70'))
    
    # ============================================
    # Gas Configuration
    # ============================================
    
    @staticmethod
    def get_max_gas_price_gwei() -> float:
        return float(os.getenv('MAX_GAS_PRICE_GWEI', '300'))
    
    @staticmethod
    def get_target_gas_price_gwei() -> float:
        return float(os.getenv('TARGET_GAS_PRICE_GWEI', '50'))
    
    @staticmethod
    def get_min_gas_price_gwei() -> float:
        return float(os.getenv('MIN_GAS_PRICE_GWEI', '10'))
    
    @staticmethod
    def get_default_gas_limit() -> int:
        return int(os.getenv('DEFAULT_GAS_LIMIT', '500000'))
    
    @staticmethod
    def get_use_dynamic_gas() -> bool:
        return os.getenv('USE_DYNAMIC_GAS', 'true').lower() == 'true'
    
    # ============================================
    # Execution Configuration
    # ============================================
    
    @staticmethod
    def get_confirmation_blocks() -> int:
        return int(os.getenv('CONFIRMATION_BLOCKS', '2'))
    
    @staticmethod
    def get_tx_timeout_seconds() -> int:
        return int(os.getenv('TX_TIMEOUT_SECONDS', '300'))
    
    @staticmethod
    def get_max_slippage() -> float:
        return float(os.getenv('MAX_SLIPPAGE', '0.005'))
    
    @staticmethod
    def get_use_flashbots() -> bool:
        return os.getenv('USE_FLASHBOTS', 'true').lower() == 'true'
    
    @staticmethod
    def get_flashbots_rpc() -> str:
        return os.getenv('FLASHBOTS_RPC', 'https://rpc.flashbots.net')
    
    # ============================================
    # Monitoring & Alerts
    # ============================================
    
    @staticmethod
    def get_telegram_bot_token() -> str:
        return os.getenv('TELEGRAM_BOT_TOKEN', '')
    
    @staticmethod
    def get_telegram_chat_id() -> str:
        return os.getenv('TELEGRAM_CHAT_ID', '')
    
    @staticmethod
    def get_enable_telegram_alerts() -> bool:
        return os.getenv('ENABLE_TELEGRAM_ALERTS', 'false').lower() == 'true'
    
    @staticmethod
    def get_discord_webhook_url() -> str:
        return os.getenv('DISCORD_WEBHOOK_URL', '')
    
    @staticmethod
    def get_enable_discord_alerts() -> bool:
        return os.getenv('ENABLE_DISCORD_ALERTS', 'false').lower() == 'true'
    
    # ============================================
    # Logging & Telemetry
    # ============================================
    
    @staticmethod
    def get_log_level() -> str:
        return os.getenv('LOG_LEVEL', 'INFO')
    
    @staticmethod
    def get_log_file() -> str:
        return os.getenv('LOG_FILE', 'logs/mega_defi.log')
    
    @staticmethod
    def get_enable_file_logging() -> bool:
        return os.getenv('ENABLE_FILE_LOGGING', 'true').lower() == 'true'
    
    @staticmethod
    def get_enable_console_logging() -> bool:
        return os.getenv('ENABLE_CONSOLE_LOGGING', 'true').lower() == 'true'
    
    @staticmethod
    def get_enable_metrics() -> bool:
        return os.getenv('ENABLE_METRICS', 'true').lower() == 'true'
    
    # ============================================
    # Development & Testing
    # ============================================
    
    @staticmethod
    def get_environment() -> str:
        return os.getenv('ENVIRONMENT', 'production')
    
    @staticmethod
    def get_debug_mode() -> bool:
        return os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    
    @staticmethod
    def get_dry_run() -> bool:
        return os.getenv('DRY_RUN', 'false').lower() == 'true'
    
    @staticmethod
    def get_test_mode() -> bool:
        return os.getenv('TEST_MODE', 'false').lower() == 'true'
    
    # ============================================
    # Utility Methods
    # ============================================
    
    @staticmethod
    def get_rpc_url() -> str:
        """Get primary RPC URL (Ethereum by default)."""
        return Config.get_ethereum_rpc_url()
    
    @staticmethod
    def get_all_rpc_urls() -> Dict[str, str]:
        """Get all configured RPC URLs."""
        return {
            'ethereum': Config.get_ethereum_rpc_url(),
            'bsc': Config.get_bsc_rpc_url(),
            'polygon': Config.get_polygon_rpc_url(),
            'arbitrum': Config.get_arbitrum_rpc_url(),
            'optimism': Config.get_optimism_rpc_url(),
        }
    
    @staticmethod
    def get_risk_params() -> Dict[str, Any]:
        """Get all risk management parameters."""
        return {
            'max_portfolio_exposure': Config.get_max_portfolio_exposure(),
            'max_position_size': Config.get_max_position_size(),
            'min_position_size': Config.get_min_position_size(),
            'max_risk_per_trade': Config.get_max_risk_per_trade(),
            'min_risk_reward_ratio': Config.get_min_risk_reward_ratio(),
            'max_daily_loss': Config.get_max_daily_loss(),
            'default_stop_loss_pct': Config.get_default_stop_loss_pct(),
            'default_take_profit_pct': Config.get_default_take_profit_pct(),
        }
    
    @staticmethod
    def is_production() -> bool:
        """Check if running in production environment."""
        return Config.get_environment().lower() == 'production'
    
    @staticmethod
    def validate_config() -> Dict[str, Any]:
        """Validate configuration and return status."""
        issues = []
        warnings = []
        
        # Check critical settings
        if not Config.get_ethereum_rpc_url():
            warnings.append("No Ethereum RPC URL configured")
        
        if not Config.get_private_key() and not Config.get_test_mode():
            warnings.append("No private key configured (required for live trading)")
        
        if not Config.get_wallet_address() and not Config.get_test_mode():
            warnings.append("No wallet address configured")
        
        # Check risk parameters are within reasonable ranges
        if Config.get_max_position_size() > 0.5:
            warnings.append("Max position size is very high (>50%)")
        
        if Config.get_max_risk_per_trade() > 0.1:
            warnings.append("Max risk per trade is very high (>10%)")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
        }


# Convenience instance for direct access
config = Config()
