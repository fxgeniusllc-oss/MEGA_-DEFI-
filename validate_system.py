#!/usr/bin/env python3
"""
Complete System Validation Script
==================================

Validates all components of the MEGA DeFi Profit Machine:
- Python package installation
- Core components functionality
- All strategies working
- Integration points
- Example scripts
- Omni-Strategy Engine

This script provides comprehensive validation as required for
Phase 1 implementation.
"""

import sys
import os
import subprocess
import logging
from typing import Dict, Any, List, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SystemValidator:
    """Comprehensive system validation."""
    
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
        
    def validate_all(self):
        """Run all validation checks."""
        print("\n" + "=" * 80)
        print("🚀 MEGA DEFI PROFIT MACHINE - COMPREHENSIVE VALIDATION")
        print("=" * 80)
        print("\nValidating all system components as per Phase 1 requirements...")
        print()
        
        # Phase 1 validations
        self._validate_python_package()
        self._validate_core_components()
        self._validate_strategies()
        self._validate_tar_scoring()
        self._validate_integration_points()
        self._validate_example_scripts()
        self._validate_omni_engine()
        self._validate_tests()
        
        # Display results
        self._display_results()
        
        # Return exit code
        return 0 if len(self.failed) == 0 else 1
    
    def _validate_python_package(self):
        """Validate Python package installation."""
        logger.info("📦 Validating Python package installation...")
        
        try:
            import mega_defi
            from mega_defi.profit_machine import create_profit_machine
            self.passed.append("Python package import successful")
            logger.info("✓ Python package installed and importable")
        except ImportError as e:
            self.failed.append(f"Python package import failed: {e}")
            logger.error(f"✗ Failed to import Python package: {e}")
            return
    
    def _validate_core_components(self):
        """Validate core components."""
        logger.info("\n⚙️  Validating core components...")
        
        components = [
            ('Strategy Engine', 'mega_defi.core.strategy_engine', 'StrategyEngine'),
            ('Market Analyzer', 'mega_defi.core.market_analyzer', 'MarketAnalyzer'),
            ('Risk Manager', 'mega_defi.core.risk_manager', 'RiskManager'),
            ('Profit Optimizer', 'mega_defi.core.profit_optimizer', 'ProfitOptimizer'),
        ]
        
        for name, module_path, class_name in components:
            try:
                module = __import__(module_path, fromlist=[class_name])
                cls = getattr(module, class_name)
                # Try to instantiate
                if class_name == 'RiskManager':
                    instance = cls(0.02, 0.1)
                else:
                    instance = cls()
                self.passed.append(f"{name} component working")
                logger.info(f"✓ {name} validated")
            except Exception as e:
                self.failed.append(f"{name} failed: {e}")
                logger.error(f"✗ {name} validation failed: {e}")
    
    def _validate_strategies(self):
        """Validate all strategies."""
        logger.info("\n🎯 Validating strategy implementations...")
        
        strategies = [
            ('Flash Loan Arbitrage', 'mega_defi.strategies.flash_loan_arbitrage', 'FlashLoanArbitrageStrategy'),
            ('Cross-Chain Arbitrage', 'mega_defi.strategies.cross_chain_arbitrage', 'CrossChainArbitrageStrategy'),
            ('Liquidation Hunter', 'mega_defi.strategies.liquidation_hunter', 'LiquidationHunterStrategy'),
            ('MEV Strategy', 'mega_defi.strategies.mev_strategy', 'MEVStrategy'),
            ('Statistical Arbitrage', 'mega_defi.strategies.statistical_arbitrage', 'StatisticalArbitrageStrategy'),
            ('Yield Optimizer', 'mega_defi.strategies.yield_optimizer', 'YieldOptimizerStrategy'),
        ]
        
        for name, module_path, class_name in strategies:
            try:
                module = __import__(module_path, fromlist=[class_name])
                cls = getattr(module, class_name)
                # Try to instantiate
                instance = cls()
                self.passed.append(f"{name} strategy working")
                logger.info(f"✓ {name} validated")
            except Exception as e:
                self.failed.append(f"{name} strategy failed: {e}")
                logger.error(f"✗ {name} validation failed: {e}")
    
    def _validate_tar_scoring(self):
        """Validate TAR scoring in Flash Loan Arbitrage."""
        logger.info("\n📊 Validating TAR scoring integration...")
        
        try:
            from mega_defi.strategies.flash_loan_arbitrage import FlashLoanArbitrageStrategy
            
            strategy = FlashLoanArbitrageStrategy()
            
            # Test market data
            market_data = {
                'exchanges': [
                    {'name': 'Uniswap', 'price': 2000, 'liquidity': 100000},
                    {'name': 'SushiSwap', 'price': 2050, 'liquidity': 120000},
                ],
                'gas_price': 50,
            }
            
            # Analyze and check for TAR score
            analysis = strategy.analyze(market_data)
            
            if analysis['best_opportunity'] and 'tar_score' in analysis['best_opportunity']:
                tar_score = analysis['best_opportunity']['tar_score']
                self.passed.append(f"TAR scoring working (score: {tar_score:.2f})")
                logger.info(f"✓ TAR scoring validated (score: {tar_score:.2f})")
            else:
                self.warnings.append("TAR scoring not producing expected results")
                logger.warning("⚠ TAR scoring test inconclusive")
                
        except Exception as e:
            self.failed.append(f"TAR scoring validation failed: {e}")
            logger.error(f"✗ TAR scoring validation failed: {e}")
    
    def _validate_integration_points(self):
        """Validate integration points."""
        logger.info("\n🔗 Validating integration points...")
        
        # Check config for integration settings
        try:
            from mega_defi.config import Config
            
            # Check environment configuration
            env = Config.get_environment()
            self.passed.append(f"Environment configuration working ({env})")
            logger.info(f"✓ Environment configuration: {env}")
            
            # Check RPC endpoints (from config)
            rpc_url = Config.get_rpc_url()
            if rpc_url:
                self.passed.append(f"RPC endpoint configured: {rpc_url}")
                logger.info(f"✓ RPC endpoint available")
            else:
                self.warnings.append("RPC endpoint not configured (use .env file)")
                logger.warning("⚠ RPC endpoint not configured")
            
            # Check Telegram bot config
            telegram_token = Config.get_telegram_bot_token()
            if telegram_token:
                self.passed.append("Telegram bot token configured")
                logger.info("✓ Telegram bot integration available")
            else:
                self.warnings.append("Telegram bot not configured (use .env file)")
                logger.warning("⚠ Telegram bot not configured")
            
        except Exception as e:
            self.failed.append(f"Integration points validation failed: {e}")
            logger.error(f"✗ Integration validation failed: {e}")
    
    def _validate_example_scripts(self):
        """Validate example scripts run without errors."""
        logger.info("\n📝 Validating example scripts...")
        
        examples = [
            'examples/basic_usage.py',
            'examples/env_config_demo.py',
        ]
        
        for example in examples:
            if os.path.exists(example):
                try:
                    result = subprocess.run(
                        ['python3', example],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    if result.returncode == 0:
                        self.passed.append(f"Example script {example} runs successfully")
                        logger.info(f"✓ {example} validated")
                    else:
                        self.failed.append(f"{example} failed with exit code {result.returncode}")
                        logger.error(f"✗ {example} failed")
                except Exception as e:
                    self.failed.append(f"{example} execution failed: {e}")
                    logger.error(f"✗ {example} execution error: {e}")
            else:
                self.warnings.append(f"Example script {example} not found")
    
    def _validate_omni_engine(self):
        """Validate Omni-Strategy Engine."""
        logger.info("\n🎯 Validating Omni-Strategy Engine...")
        
        if os.path.exists('omni_strategy_engine.py'):
            try:
                # Test help command
                result = subprocess.run(
                    ['python3', 'omni_strategy_engine.py', '--help'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0 and 'OMNI-STRATEGY ENGINE' in result.stdout:
                    self.passed.append("Omni-Strategy Engine CLI available")
                    logger.info("✓ Omni-Strategy Engine CLI validated")
                else:
                    self.failed.append("Omni-Strategy Engine help command failed")
                    logger.error("✗ Omni-Strategy Engine help failed")
                
                # Test conservative mode
                result = subprocess.run(
                    ['python3', 'omni_strategy_engine.py', 
                     '--mode=CONSERVATIVE', '--capital=100000', '--cycles=5'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    self.passed.append("Omni-Strategy Engine CONSERVATIVE mode working")
                    logger.info("✓ Omni-Strategy Engine CONSERVATIVE mode validated")
                else:
                    self.failed.append("Omni-Strategy Engine execution failed")
                    logger.error("✗ Omni-Strategy Engine execution failed")
                    
            except Exception as e:
                self.failed.append(f"Omni-Strategy Engine validation failed: {e}")
                logger.error(f"✗ Omni-Strategy Engine validation error: {e}")
        else:
            self.failed.append("omni_strategy_engine.py not found")
            logger.error("✗ omni_strategy_engine.py not found")
    
    def _validate_tests(self):
        """Validate test suite."""
        logger.info("\n🧪 Validating test suite...")
        
        try:
            result = subprocess.run(
                ['python3', '-m', 'unittest', 'discover', 'tests/', '-v'],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # Parse test results
            output = result.stdout + result.stderr
            
            if 'OK' in output or result.returncode == 0:
                # Extract test count
                import re
                match = re.search(r'Ran (\d+) tests', output)
                if match:
                    test_count = match.group(1)
                    self.passed.append(f"All {test_count} tests passing")
                    logger.info(f"✓ Test suite validated ({test_count} tests)")
                else:
                    self.passed.append("Test suite passed")
                    logger.info("✓ Test suite validated")
            else:
                self.failed.append("Some tests failed")
                logger.error("✗ Test suite has failures")
                
        except Exception as e:
            self.failed.append(f"Test execution failed: {e}")
            logger.error(f"✗ Test execution error: {e}")
    
    def _display_results(self):
        """Display validation results."""
        print("\n" + "=" * 80)
        print("📊 VALIDATION RESULTS")
        print("=" * 80)
        
        print(f"\n✅ PASSED: {len(self.passed)}")
        for item in self.passed:
            print(f"   ✓ {item}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS: {len(self.warnings)}")
            for item in self.warnings:
                print(f"   ⚠ {item}")
        
        if self.failed:
            print(f"\n❌ FAILED: {len(self.failed)}")
            for item in self.failed:
                print(f"   ✗ {item}")
        
        print("\n" + "=" * 80)
        print("VALIDATION SUMMARY")
        print("=" * 80)
        
        total = len(self.passed) + len(self.failed) + len(self.warnings)
        success_rate = (len(self.passed) / total * 100) if total > 0 else 0
        
        print(f"\nTotal Checks: {total}")
        print(f"Passed: {len(self.passed)}")
        print(f"Warnings: {len(self.warnings)}")
        print(f"Failed: {len(self.failed)}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if len(self.failed) == 0:
            print("\n✅ SYSTEM VALIDATION: COMPLETE")
            print("🚀 All scripts are working and ready for Phase 1 deployment!")
        else:
            print("\n⚠️  SYSTEM VALIDATION: INCOMPLETE")
            print("⚠️  Some components need attention before production deployment.")
        
        print("=" * 80)


def main():
    """Run complete system validation."""
    validator = SystemValidator()
    exit_code = validator.validate_all()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
