#!/usr/bin/env python3
"""
Environment Configuration Demo
==============================

Demonstrates how the MEGA DeFi system loads and uses environment variables.

Note: This example assumes the package is installed with 'pip install -e .'
If you haven't installed the package yet, run: pip install -e .
"""

from mega_defi.config import Config
from mega_defi.profit_machine import create_profit_machine


def demonstrate_config_loading():
    """Demonstrate configuration loading from environment."""
    print("\n" + "=" * 70)
    print("ENVIRONMENT CONFIGURATION DEMONSTRATION")
    print("=" * 70)
    
    # Check if .env file exists
    import pathlib
    env_file = pathlib.Path(__file__).parent.parent / '.env'
    
    if env_file.exists():
        print(f"\n✅ .env file found at: {env_file}")
    else:
        print(f"\n⚠️  No .env file found. Using default configuration.")
        print(f"   Copy .env.example to .env to customize settings:")
        print(f"   cp .env.example .env")
    
    print("\n" + "-" * 70)
    print("CONFIGURATION VALUES")
    print("-" * 70)
    
    # Display Environment Settings
    print(f"\n🌍 Environment Settings:")
    print(f"   Environment: {Config.get_environment()}")
    print(f"   Debug Mode: {Config.get_debug_mode()}")
    print(f"   Dry Run: {Config.get_dry_run()}")
    print(f"   Test Mode: {Config.get_test_mode()}")
    
    # Display Network Configuration
    print(f"\n🌐 Network Configuration:")
    print(f"   Ethereum RPC: {Config.get_ethereum_rpc_url()}")
    print(f"   BSC RPC: {Config.get_bsc_rpc_url()}")
    print(f"   Polygon RPC: {Config.get_polygon_rpc_url()}")
    print(f"   Arbitrum RPC: {Config.get_arbitrum_rpc_url()}")
    
    # Display API Keys (masked)
    print(f"\n🔑 API Keys:")
    alchemy_key = Config.get_alchemy_api_key()
    print(f"   Alchemy: {'[SET]' if alchemy_key else '[NOT SET]'}")
    infura_key = Config.get_infura_api_key()
    print(f"   Infura: {'[SET]' if infura_key else '[NOT SET]'}")
    etherscan_key = Config.get_etherscan_api_key()
    print(f"   Etherscan: {'[SET]' if etherscan_key else '[NOT SET]'}")
    coingecko_key = Config.get_coingecko_api_key()
    print(f"   CoinGecko: {'[SET]' if coingecko_key else '[NOT SET]'}")
    
    # Display Wallet Configuration (masked)
    print(f"\n💼 Wallet Configuration:")
    private_key = Config.get_private_key()
    print(f"   Private Key: {'[SET]' if private_key else '[NOT SET]'}")
    wallet = Config.get_wallet_address()
    print(f"   Wallet Address: {wallet if wallet else '[NOT SET]'}")
    
    # Display Risk Parameters
    print(f"\n🛡️ Risk Management:")
    print(f"   Initial Portfolio: ${Config.get_initial_portfolio_value():,.2f}")
    print(f"   Max Portfolio Exposure: {Config.get_max_portfolio_exposure()*100:.1f}%")
    print(f"   Max Position Size: {Config.get_max_position_size()*100:.1f}%")
    print(f"   Max Risk Per Trade: {Config.get_max_risk_per_trade()*100:.1f}%")
    print(f"   Min Risk/Reward: {Config.get_min_risk_reward_ratio():.1f}")
    print(f"   Stop Loss: {Config.get_default_stop_loss_pct()*100:.1f}%")
    print(f"   Take Profit: {Config.get_default_take_profit_pct()*100:.1f}%")
    
    # Display Strategy Parameters
    print(f"\n🎯 Strategy Parameters:")
    print(f"   Flash Loan Min Profit: {Config.get_flash_loan_min_profit()*100:.2f}%")
    print(f"   Arbitrage Max Gas: ${Config.get_arbitrage_max_gas_cost():.0f}")
    print(f"   Cross-Chain Min Profit: {Config.get_cross_chain_min_profit()*100:.2f}%")
    print(f"   Liquidation Min Health: {Config.get_liquidation_min_health_factor():.2f}")
    print(f"   MEV Min Tx Size: ${Config.get_mev_min_transaction_size():,.0f}")
    
    # Display Gas Configuration
    print(f"\n⛽ Gas Configuration:")
    print(f"   Max Gas Price: {Config.get_max_gas_price_gwei():.0f} gwei")
    print(f"   Target Gas Price: {Config.get_target_gas_price_gwei():.0f} gwei")
    print(f"   Min Gas Price: {Config.get_min_gas_price_gwei():.0f} gwei")
    print(f"   Use Dynamic Gas: {Config.get_use_dynamic_gas()}")
    print(f"   Default Gas Limit: {Config.get_default_gas_limit():,}")
    
    # Display Monitoring Configuration
    print(f"\n🔔 Monitoring & Alerts:")
    telegram_token = Config.get_telegram_bot_token()
    print(f"   Telegram Bot: {'[CONFIGURED]' if telegram_token else '[NOT CONFIGURED]'}")
    print(f"   Telegram Alerts: {'ENABLED' if Config.get_enable_telegram_alerts() else 'DISABLED'}")
    discord_webhook = Config.get_discord_webhook_url()
    print(f"   Discord Webhook: {'[CONFIGURED]' if discord_webhook else '[NOT CONFIGURED]'}")
    
    # Display Logging Configuration
    print(f"\n📊 Logging:")
    print(f"   Log Level: {Config.get_log_level()}")
    print(f"   Log File: {Config.get_log_file()}")
    print(f"   File Logging: {'ENABLED' if Config.get_enable_file_logging() else 'DISABLED'}")
    print(f"   Console Logging: {'ENABLED' if Config.get_enable_console_logging() else 'DISABLED'}")
    print(f"   Metrics: {'ENABLED' if Config.get_enable_metrics() else 'DISABLED'}")


def demonstrate_config_validation():
    """Demonstrate configuration validation."""
    print("\n" + "-" * 70)
    print("CONFIGURATION VALIDATION")
    print("-" * 70)
    
    validation = Config.validate_config()
    
    print(f"\n✓ Validation Status: {'PASSED' if validation['valid'] else 'FAILED'}")
    
    if validation['issues']:
        print(f"\n❌ Critical Issues Found:")
        for issue in validation['issues']:
            print(f"   • {issue}")
    else:
        print(f"\n✅ No critical issues found")
    
    if validation['warnings']:
        print(f"\n⚠️  Warnings:")
        for warning in validation['warnings']:
            print(f"   • {warning}")
    else:
        print(f"\n✅ No warnings")


def demonstrate_profit_machine_with_config():
    """Demonstrate creating Profit Machine with config."""
    print("\n" + "-" * 70)
    print("PROFIT MACHINE INITIALIZATION WITH CONFIG")
    print("-" * 70)
    
    print("\nInitializing Profit Machine using environment configuration...")
    
    # Create profit machine - it will automatically use config values
    machine = create_profit_machine()
    
    print("\n✅ Profit Machine initialized successfully!")
    print("\nThe machine is using the following configuration:")
    print(f"   • Portfolio value from config: ${Config.get_initial_portfolio_value():,.2f}")
    print(f"   • Risk per trade from config: {Config.get_max_risk_per_trade()*100:.1f}%")
    print(f"   • Position size from config: {Config.get_max_position_size()*100:.1f}%")
    
    # Get performance report
    report = machine.get_performance_report()
    portfolio = report['portfolio_status']
    print(f"\n📊 Portfolio Status:")
    print(f"   Value: ${portfolio['portfolio_value']:,.2f}")
    print(f"   Available Capacity: {portfolio['available_capacity']:.2%}")


def demonstrate_custom_override():
    """Demonstrate overriding config with custom values."""
    print("\n" + "-" * 70)
    print("CUSTOM CONFIGURATION OVERRIDE")
    print("-" * 70)
    
    print("\nYou can override config values when creating the Profit Machine:")
    
    # Override specific values
    custom_machine = create_profit_machine(
        portfolio_value=50000,    # Override default
        max_risk_per_trade=0.01,  # More conservative
        max_position_size=0.15    # Smaller positions
    )
    
    print("\n✅ Profit Machine created with custom overrides!")
    print("   • Portfolio: $50,000 (overridden)")
    print("   • Risk per trade: 1% (overridden)")
    print("   • Max position: 15% (overridden)")
    
    report = custom_machine.get_performance_report()
    portfolio = report['portfolio_status']
    print(f"\n📊 Custom Portfolio Status:")
    print(f"   Value: ${portfolio['portfolio_value']:,.2f}")


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 70)
    print("🚀 MEGA DEFI PROFIT MACHINE")
    print("   ENVIRONMENT CONFIGURATION DEMONSTRATION")
    print("=" * 70)
    
    # Demonstrate config loading
    demonstrate_config_loading()
    
    # Demonstrate validation
    demonstrate_config_validation()
    
    # Demonstrate profit machine with config
    demonstrate_profit_machine_with_config()
    
    # Demonstrate custom override
    demonstrate_custom_override()
    
    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)
    print("\n💡 Key Takeaways:")
    print("   1. Create .env file from .env.example to customize configuration")
    print("   2. All modules automatically load values from environment variables")
    print("   3. You can still override values programmatically when needed")
    print("   4. Configuration is validated on startup")
    print("   5. Sensitive data (keys) is kept separate from code")
    
    print("\n📚 For more information:")
    print("   • See ENV_CONFIG_GUIDE.md for complete configuration guide")
    print("   • See .env.example for all available options")
    print("   • See README.md for system overview")
    
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
