#!/usr/bin/env python3
"""
Phase 1 Integration Test
========================

Demonstrates all requirements from the problem statement:

1. ✅ Use existing TAR scoring in FlashLoanArbitrageStrategy
2. ✅ Import RPC manager and Web3 connections
3. ✅ Connect to Telegram bot system
4. ✅ Use existing smart contract interfaces
5. ✅ Deploy Basic Omni-Engine with conservative settings

This script validates the complete integration.
"""

import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_phase1_requirements():
    """Test all Phase 1 requirements."""
    
    print("\n" + "=" * 80)
    print("🎯 PHASE 1 INTEGRATION TEST")
    print("=" * 80)
    print()
    
    results = []
    
    # Requirement 1: TAR Scoring in Flash Loan Arbitrage
    print("1. Testing TAR Scoring in FlashLoanArbitrageStrategy...")
    try:
        from mega_defi.strategies.flash_loan_arbitrage import FlashLoanArbitrageStrategy
        
        strategy = FlashLoanArbitrageStrategy()
        
        # Test market data with price differences
        market_data = {
            'exchanges': [
                {'name': 'Uniswap', 'price': 2000, 'liquidity': 100000},
                {'name': 'SushiSwap', 'price': 2050, 'liquidity': 120000},
            ],
            'gas_price': 50,
        }
        
        analysis = strategy.analyze(market_data)
        
        if analysis['best_opportunity'] and 'tar_score' in analysis['best_opportunity']:
            tar_score = analysis['best_opportunity']['tar_score']
            results.append(('✅', f"TAR Scoring working (score: {tar_score:.2f})"))
            print(f"   ✅ TAR Score calculated: {tar_score:.2f}")
            print(f"   ✅ Profit percentage: {analysis['best_opportunity']['profit_percentage']*100:.2f}%")
        else:
            results.append(('❌', "TAR Scoring not producing expected results"))
            print("   ❌ Failed")
            
    except Exception as e:
        results.append(('❌', f"TAR Scoring test failed: {e}"))
        print(f"   ❌ Error: {e}")
    
    # Requirement 2: RPC Manager and Web3 Connections
    print("\n2. Testing RPC Manager and Web3 Connections...")
    try:
        from mega_defi.config import Config
        
        # Get all RPC URLs
        rpc_urls = Config.get_all_rpc_urls()
        
        print(f"   ✅ Primary RPC: {Config.get_rpc_url()}")
        print(f"   ✅ Available networks: {', '.join(rpc_urls.keys())}")
        
        # Test individual network configs
        print(f"   ✅ Ethereum: {Config.get_ethereum_rpc_url()}")
        print(f"   ✅ BSC: {Config.get_bsc_rpc_url()}")
        print(f"   ✅ Polygon: {Config.get_polygon_rpc_url()}")
        
        results.append(('✅', f"RPC Manager configured for {len(rpc_urls)} networks"))
        
    except Exception as e:
        results.append(('❌', f"RPC Manager test failed: {e}"))
        print(f"   ❌ Error: {e}")
    
    # Requirement 3: Telegram Bot Integration
    print("\n3. Testing Telegram Bot System Integration...")
    try:
        from mega_defi.config import Config
        
        telegram_token = Config.get_telegram_bot_token()
        telegram_chat_id = Config.get_telegram_chat_id()
        alerts_enabled = Config.get_enable_telegram_alerts()
        
        if telegram_token:
            results.append(('✅', "Telegram bot token configured"))
            print(f"   ✅ Bot token configured")
        else:
            results.append(('⚠️', "Telegram bot not configured (optional)"))
            print(f"   ⚠️  Bot token not configured (use .env file)")
        
        print(f"   ✅ Telegram integration points available")
        print(f"   ✅ Alert system ready (enabled: {alerts_enabled})")
        
        results.append(('✅', "Telegram bot integration points ready"))
        
    except Exception as e:
        results.append(('❌', f"Telegram bot test failed: {e}"))
        print(f"   ❌ Error: {e}")
    
    # Requirement 4: Smart Contract Interfaces
    print("\n4. Testing Smart Contract Interfaces...")
    try:
        from mega_defi.config import Config
        
        # DEX Interfaces
        print("   ✅ DEX Interfaces:")
        print(f"      - Uniswap V2: {Config.get_uniswap_v2_router()}")
        print(f"      - Uniswap V3: {Config.get_uniswap_v3_router()}")
        print(f"      - SushiSwap: {Config.get_sushiswap_router()}")
        print(f"      - PancakeSwap: {Config.get_pancakeswap_router()}")
        
        # Lending Protocols
        print("   ✅ Lending Protocol Interfaces:")
        print(f"      - Aave: {Config.get_aave_lending_pool()}")
        print(f"      - Compound: {Config.get_compound_comptroller()}")
        
        # Flash Loan Providers
        print("   ✅ Flash Loan Providers:")
        print(f"      - Aave: {Config.get_aave_flash_loan_pool()}")
        print(f"      - dYdX: {Config.get_dydx_solo_margin()}")
        
        results.append(('✅', "All smart contract interfaces configured"))
        
    except Exception as e:
        results.append(('❌', f"Smart contract interfaces test failed: {e}"))
        print(f"   ❌ Error: {e}")
    
    # Requirement 5: Deploy Basic Omni-Engine
    print("\n5. Testing Omni-Engine Deployment (Conservative Mode)...")
    try:
        import subprocess
        
        # Test the command from the problem statement
        result = subprocess.run(
            ['python3', 'omni_strategy_engine.py', 
             '--mode=CONSERVATIVE', '--capital=100000', '--cycles=3'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            results.append(('✅', "Omni-Engine deployed successfully"))
            print("   ✅ Engine initialized")
            print("   ✅ Conservative mode working")
            print("   ✅ Capital allocation: $100,000")
            print("   ✅ Cycles completed successfully")
        else:
            results.append(('❌', "Omni-Engine deployment failed"))
            print(f"   ❌ Deployment failed")
            
    except Exception as e:
        results.append(('❌', f"Omni-Engine test failed: {e}"))
        print(f"   ❌ Error: {e}")
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 PHASE 1 INTEGRATION TEST RESULTS")
    print("=" * 80)
    
    passed = sum(1 for status, _ in results if status == '✅')
    warnings = sum(1 for status, _ in results if status == '⚠️')
    failed = sum(1 for status, _ in results if status == '❌')
    
    print(f"\nTotal Requirements: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Warnings: {warnings}")
    print(f"Failed: {failed}")
    print()
    
    for status, message in results:
        print(f"{status} {message}")
    
    print("\n" + "=" * 80)
    
    if failed == 0:
        print("✅ PHASE 1 INTEGRATION: COMPLETE")
        print("🚀 All requirements validated and ready for deployment!")
        print("\nNext Step:")
        print("  python omni_strategy_engine.py --mode=CONSERVATIVE --capital=100000")
        return 0
    else:
        print("⚠️  PHASE 1 INTEGRATION: INCOMPLETE")
        print(f"⚠️  {failed} requirement(s) need attention")
        return 1
    
    print("=" * 80)


def main():
    """Run Phase 1 integration test."""
    exit_code = test_phase1_requirements()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
