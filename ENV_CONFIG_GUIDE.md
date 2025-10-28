# Environment Configuration Guide

## Overview

The MEGA DeFi Profit Machine uses environment variables for configuration. This allows you to:
- Keep sensitive data (API keys, private keys) separate from code
- Configure different settings for different environments (development, production)
- Easily customize behavior without modifying code

## Quick Start

### Step 1: Copy the Example File

```bash
cp .env.example .env
```

### Step 2: Edit Your Configuration

Open `.env` in your text editor and fill in your values:

```bash
# Example: Add your API keys
ALCHEMY_API_KEY=your_alchemy_api_key_here
ETHERSCAN_API_KEY=your_etherscan_api_key_here

# Example: Configure your wallet
WALLET_ADDRESS=0xYourWalletAddress
PRIVATE_KEY=0xYourPrivateKeyHere

# Example: Adjust risk parameters
INITIAL_PORTFOLIO_VALUE=50000
MAX_RISK_PER_TRADE=0.01
```

### Step 3: Never Commit .env

The `.env` file is already in `.gitignore` and should NEVER be committed to version control. It contains sensitive information!

## Configuration Categories

### 🌐 Network Configuration

Configure RPC endpoints for multiple blockchains:

```bash
# Ethereum
ETHEREUM_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY
ETHEREUM_CHAIN_ID=1

# BSC
BSC_RPC_URL=https://bsc-dataseed.binance.org/
BSC_CHAIN_ID=56

# Polygon, Arbitrum, Optimism, etc.
```

**Required for:**
- All modules that interact with blockchain networks
- Cross-chain arbitrage strategies
- Market data fetching

### 🔑 API Keys

Configure access to external services:

```bash
ALCHEMY_API_KEY=your_key
INFURA_API_KEY=your_key
ETHERSCAN_API_KEY=your_key
COINGECKO_API_KEY=your_key
THEGRAPH_API_KEY=your_key
```

**Required for:**
- RPC access to blockchain networks
- Price feed data
- Contract verification
- DeFi protocol data

### 💼 Trading Configuration

Configure your trading accounts:

```bash
PRIVATE_KEY=0xYOUR_PRIVATE_KEY_HERE
WALLET_ADDRESS=0xYOUR_WALLET_ADDRESS
TREASURY_ADDRESS=0xYOUR_TREASURY_ADDRESS
```

**⚠️ SECURITY WARNING:**
- NEVER share your private keys
- Use separate wallets for testing and production
- Consider using hardware wallets for large amounts

### 🛡️ Risk Management

Configure risk parameters:

```bash
INITIAL_PORTFOLIO_VALUE=10000
MAX_PORTFOLIO_EXPOSURE=0.80
MAX_POSITION_SIZE=0.20
MAX_RISK_PER_TRADE=0.02
MIN_RISK_REWARD_RATIO=2.0
DEFAULT_STOP_LOSS_PCT=0.10
DEFAULT_TAKE_PROFIT_PCT=0.25
```

**Affects:**
- Position sizing
- Stop loss and take profit levels
- Maximum portfolio exposure
- Risk-reward calculations

### 🎯 Strategy Configuration

Configure individual trading strategies:

```bash
# Flash Loan Arbitrage
FLASH_LOAN_MIN_PROFIT=0.005
ARBITRAGE_MAX_GAS_COST=500
ARBITRAGE_MIN_LIQUIDITY=10000

# Cross-Chain Arbitrage
CROSS_CHAIN_MIN_PROFIT=0.03
CROSS_CHAIN_MAX_BRIDGE_TIME=600

# Liquidation Hunter
LIQUIDATION_MIN_HEALTH_FACTOR=1.05
LIQUIDATION_MIN_PROFIT=0.02

# MEV Strategy
MEV_MIN_TRANSACTION_SIZE=10000
MEV_MIN_EXPECTED_PROFIT=0.01

# Yield Optimizer
YIELD_MIN_APY=0.15
YIELD_MAX_PROTOCOL_RISK=0.50
```

**Affects:**
- Strategy selection criteria
- Opportunity filtering
- Execution thresholds

### ⛽ Gas Configuration

Configure gas price strategy:

```bash
MAX_GAS_PRICE_GWEI=300
TARGET_GAS_PRICE_GWEI=50
MIN_GAS_PRICE_GWEI=10
USE_DYNAMIC_GAS=true
DEFAULT_GAS_LIMIT=500000
```

**Affects:**
- Transaction costs
- Execution speed
- Profit calculations

### 🔔 Monitoring & Alerts

Configure notifications:

```bash
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
ENABLE_TELEGRAM_ALERTS=true

# Discord
DISCORD_WEBHOOK_URL=your_webhook_url
ENABLE_DISCORD_ALERTS=false

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
ENABLE_EMAIL_ALERTS=false
```

**Enables:**
- Real-time trade notifications
- Error alerts
- Performance reports

### 📊 Logging & Telemetry

Configure logging behavior:

```bash
LOG_LEVEL=INFO
LOG_FILE=logs/mega_defi.log
ENABLE_FILE_LOGGING=true
ENABLE_CONSOLE_LOGGING=true
ENABLE_METRICS=true
```

**Affects:**
- Log detail level (DEBUG, INFO, WARNING, ERROR)
- Where logs are stored
- Performance metrics tracking

### 🧪 Development & Testing

Configure development environment:

```bash
ENVIRONMENT=production
DEBUG_MODE=false
DRY_RUN=false
TEST_MODE=false
```

**Use cases:**
- `DRY_RUN=true` - Test strategies without executing real transactions
- `TEST_MODE=true` - Use test networks and mock data
- `DEBUG_MODE=true` - Enable detailed debugging output

## Usage in Code

### Python

```python
from mega_defi.config import Config

# Access configuration
rpc_url = Config.get_ethereum_rpc_url()
portfolio_value = Config.get_initial_portfolio_value()
max_risk = Config.get_max_risk_per_trade()

# Get all RPC URLs
rpc_urls = Config.get_all_rpc_urls()

# Get all risk parameters
risk_params = Config.get_risk_params()

# Validate configuration
validation = Config.validate_config()
if not validation['valid']:
    print("Configuration errors:", validation['issues'])
if validation['warnings']:
    print("Configuration warnings:", validation['warnings'])
```

### TypeScript

```typescript
import { Config } from './config.js';

// Access configuration
const rpcUrl = Config.getEthereumRpcUrl();
const portfolioValue = Config.getInitialPortfolioValue();
const maxRisk = Config.getMaxRiskPerTrade();

// Get all RPC URLs
const rpcUrls = Config.getAllRpcUrls();

// Get all risk parameters
const riskParams = Config.getRiskParams();

// Validate configuration
const validation = Config.validateConfig();
if (!validation.valid) {
    console.error('Configuration errors:', validation.issues);
}
if (validation.warnings.length > 0) {
    console.warn('Configuration warnings:', validation.warnings);
}
```

## Configuration Defaults

All configuration values have sensible defaults. If you don't provide a value in `.env`, the system will use the default:

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `INITIAL_PORTFOLIO_VALUE` | 10000 | Starting portfolio value in USD |
| `MAX_RISK_PER_TRADE` | 0.02 | Maximum 2% risk per trade |
| `MAX_POSITION_SIZE` | 0.20 | Maximum 20% of portfolio per position |
| `ARBITRAGE_MIN_PROFIT` | 0.005 | Minimum 0.5% profit for arbitrage |
| `LOG_LEVEL` | INFO | Logging detail level |
| `ENVIRONMENT` | production | Environment mode |

See `.env.example` for complete list of defaults.

## Environment Modes

### Production Mode (default)

```bash
ENVIRONMENT=production
DEBUG_MODE=false
DRY_RUN=false
```

- Uses real API keys and private keys
- Executes actual transactions
- Minimal logging

### Development Mode

```bash
ENVIRONMENT=development
DEBUG_MODE=true
DRY_RUN=true
```

- Can use test networks
- Simulates transactions without execution
- Detailed debug logging

### Testing Mode

```bash
ENVIRONMENT=testing
TEST_MODE=true
MOCK_TRANSACTIONS=true
```

- Uses mock data
- No real API calls
- For automated testing

## Best Practices

### 1. Use Multiple .env Files

Create separate configuration files for different environments:

```bash
.env              # Production (never commit)
.env.development  # Development settings
.env.testing      # Test settings
```

### 2. Secure Your Private Keys

```bash
# ❌ BAD - Never hardcode keys
PRIVATE_KEY=0x123abc...

# ✅ GOOD - Use environment variable or key management service
# Set via command line or secure key manager
```

### 3. Start with Conservative Settings

```bash
# Start with low risk
INITIAL_PORTFOLIO_VALUE=1000
MAX_RISK_PER_TRADE=0.01
MAX_POSITION_SIZE=0.05
DRY_RUN=true

# Increase gradually after testing
```

### 4. Use Dry Run Mode First

```bash
# Test your configuration without risking funds
DRY_RUN=true
```

Run the system and verify:
- Strategies are working correctly
- Risk parameters are appropriate
- Opportunities are being identified

Then set `DRY_RUN=false` when ready for live trading.

### 5. Monitor Your Configuration

```bash
# Enable comprehensive logging
LOG_LEVEL=INFO
ENABLE_FILE_LOGGING=true
ENABLE_METRICS=true

# Enable alerts
ENABLE_TELEGRAM_ALERTS=true
```

### 6. Regularly Rotate Keys

- Change API keys monthly
- Use different keys for different risk levels
- Audit key usage regularly

## Validation

The system automatically validates your configuration on startup:

```python
from mega_defi.config import Config

validation = Config.validate_config()
print(f"Valid: {validation['valid']}")
print(f"Issues: {validation['issues']}")
print(f"Warnings: {validation['warnings']}")
```

Common validation checks:
- ✅ Required API keys are present (or in test mode)
- ✅ Risk parameters are within safe ranges
- ✅ Network configurations are valid
- ⚠️ Warnings for high-risk settings

## Troubleshooting

### Problem: "No .env file found"

**Solution:** Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### Problem: "Configuration errors: No private key"

**Solution:** Either:
1. Add `PRIVATE_KEY=...` to `.env`
2. Or set `TEST_MODE=true` to skip validation

### Problem: Changes to .env not taking effect

**Solution:** Restart your application. The `.env` file is loaded on startup.

### Problem: "Module 'config' not found"

**Solution:** The config modules are included in the package. Make sure you've installed with:
```bash
pip install -e .
```

## Security Checklist

- [ ] `.env` file is in `.gitignore`
- [ ] Never committed `.env` to version control
- [ ] Private keys are kept secure
- [ ] Using separate keys for test/production
- [ ] API keys have appropriate rate limits
- [ ] Regular key rotation schedule established
- [ ] Backup of configuration stored securely
- [ ] Tested with `DRY_RUN=true` first
- [ ] Monitoring and alerts configured
- [ ] Risk parameters reviewed and appropriate

## Support

For additional help:
- See [README.md](README.md) for system overview
- See [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) for setup
- Check [QUICKSTART.md](QUICKSTART.md) for quick start guide
- Review `.env.example` for all available options

---

**Remember:** Never commit your `.env` file. Always keep your private keys secure.
