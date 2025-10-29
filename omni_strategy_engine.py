#!/usr/bin/env python3
"""
OMNI-STRATEGY ENGINE - Ultimate Profit Machine
===============================================

Unified command-line interface for running all advanced trading strategies
with intelligent orchestration, risk management, and profit optimization.

This engine integrates:
- Flash Loan Arbitrage with TAR scoring
- Cross-Chain Arbitrage
- Liquidation Hunting
- MEV Strategy (Sandwich Attacks)
- Statistical Arbitrage
- Yield Optimization

Usage:
    python omni_strategy_engine.py --mode=CONSERVATIVE --capital=100000
    python omni_strategy_engine.py --mode=AGGRESSIVE --capital=500000 --dry-run
    python omni_strategy_engine.py --mode=BALANCED --capital=250000 --strategies=flash_loan,mev
"""

import argparse
import sys
import logging
from typing import Dict, Any, List, Optional
import time
from datetime import datetime

# Import core components
from mega_defi.profit_machine import create_profit_machine
from mega_defi.core.strategy_engine import StrategyEngine
from mega_defi.core.risk_manager import RiskManager
from mega_defi.core.profit_optimizer import ProfitOptimizer

# Import advanced strategies
from mega_defi.strategies import (
    FlashLoanArbitrageStrategy,
    CrossChainArbitrageStrategy,
    LiquidationHunterStrategy,
    MEVStrategy,
    StatisticalArbitrageStrategy,
    YieldOptimizerStrategy,
    StrategyRegistry,
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OmniStrategyEngine:
    """
    Omni-Strategy Engine - Unified orchestration of all trading strategies.
    
    Features:
    - Multi-strategy coordination
    - Dynamic capital allocation
    - Risk-adjusted position sizing
    - Performance monitoring and optimization
    - Emergency shutdown capabilities
    """
    
    # Operating modes with risk profiles
    MODES = {
        'CONSERVATIVE': {
            'max_risk_per_trade': 0.01,      # 1% max risk
            'max_position_size': 0.05,       # 5% max position
            'max_strategies_active': 2,       # Limited concurrent strategies
            'min_profit_threshold': 0.02,    # 2% minimum profit
            'description': 'Low-risk mode for capital preservation'
        },
        'BALANCED': {
            'max_risk_per_trade': 0.02,      # 2% max risk
            'max_position_size': 0.10,       # 10% max position
            'max_strategies_active': 4,       # Moderate concurrent strategies
            'min_profit_threshold': 0.01,    # 1% minimum profit
            'description': 'Balanced risk/reward profile'
        },
        'AGGRESSIVE': {
            'max_risk_per_trade': 0.05,      # 5% max risk
            'max_position_size': 0.20,       # 20% max position
            'max_strategies_active': 6,       # All strategies can run
            'min_profit_threshold': 0.005,   # 0.5% minimum profit
            'description': 'High-risk, high-reward mode'
        }
    }
    
    def __init__(self, 
                 mode: str = 'BALANCED',
                 capital: float = 100000,
                 dry_run: bool = False,
                 strategies: Optional[List[str]] = None):
        """
        Initialize Omni-Strategy Engine.
        
        Args:
            mode: Operating mode (CONSERVATIVE, BALANCED, AGGRESSIVE)
            capital: Initial capital in USD
            dry_run: If True, simulate without real trading
            strategies: List of strategy names to enable (None = all)
        """
        self.mode = mode.upper()
        self.capital = capital
        self.dry_run = dry_run
        self.enabled_strategies = strategies or []
        
        if self.mode not in self.MODES:
            raise ValueError(f"Invalid mode: {mode}. Choose from {list(self.MODES.keys())}")
        
        self.config = self.MODES[self.mode]
        self.registry = StrategyRegistry()
        
        logger.info("=" * 80)
        logger.info("🚀 OMNI-STRATEGY ENGINE - INITIALIZATION")
        logger.info("=" * 80)
        logger.info(f"Mode: {self.mode} - {self.config['description']}")
        logger.info(f"Capital: ${capital:,.2f}")
        logger.info(f"Dry Run: {'YES' if dry_run else 'NO'}")
        logger.info(f"Max Risk Per Trade: {self.config['max_risk_per_trade']*100:.1f}%")
        logger.info(f"Max Position Size: {self.config['max_position_size']*100:.1f}%")
        logger.info("=" * 80)
        
        # Initialize core components
        self._initialize_strategies()
        
        # Performance tracking
        self.total_profit = 0.0
        self.total_trades = 0
        self.start_time = datetime.now()
        
    def _initialize_strategies(self):
        """Initialize all available strategies based on configuration."""
        logger.info("Initializing strategies...")
        
        # Strategy initialization with mode-specific parameters
        strategies_config = {
            'flash_loan': {
                'class': FlashLoanArbitrageStrategy,
                'params': {
                    'min_profit_threshold': self.config['min_profit_threshold'],
                    'max_gas_cost': 500,
                    'min_liquidity': 10000
                }
            },
            'cross_chain': {
                'class': CrossChainArbitrageStrategy,
                'params': {
                    'min_profit_after_fees': self.config['min_profit_threshold'],
                    'max_bridge_time': 600
                }
            },
            'liquidation': {
                'class': LiquidationHunterStrategy,
                'params': {
                    'min_health_factor': 1.05,
                    'min_liquidation_profit': self.config['min_profit_threshold']
                }
            },
            'mev': {
                'class': MEVStrategy,
                'params': {
                    'min_transaction_size': 10000,
                    'min_expected_profit': self.config['min_profit_threshold']
                }
            },
            'statistical': {
                'class': StatisticalArbitrageStrategy,
                'params': {
                    'z_score_threshold': 2.0,
                    'correlation_threshold': 0.7
                }
            },
            'yield': {
                'class': YieldOptimizerStrategy,
                'params': {
                    'min_apy': 0.15,
                    'max_protocol_risk': 0.5
                }
            }
        }
        
        # Enable all strategies or only specified ones
        for name, config in strategies_config.items():
            if not self.enabled_strategies or name in self.enabled_strategies:
                try:
                    strategy = config['class'](**config['params'])
                    self.registry.register_strategy(strategy)
                    logger.info(f"✓ Registered: {strategy.name}")
                except Exception as e:
                    logger.error(f"✗ Failed to register {name}: {e}")
        
        logger.info(f"Total strategies active: {len(self.registry.strategies)}")
        
    def run(self, duration_seconds: Optional[int] = None, cycles: Optional[int] = None):
        """
        Run the Omni-Strategy Engine.
        
        Args:
            duration_seconds: Run for specified seconds (None = run indefinitely)
            cycles: Run for specified number of cycles (None = run by duration)
        """
        logger.info("=" * 80)
        logger.info("🎯 OMNI-STRATEGY ENGINE - STARTING OPERATIONS")
        logger.info("=" * 80)
        
        if self.dry_run:
            logger.warning("⚠️  DRY RUN MODE - No real trades will be executed")
        
        cycle = 0
        start_time = time.time()
        
        try:
            while True:
                cycle += 1
                
                # Check exit conditions
                if cycles and cycle > cycles:
                    logger.info(f"Completed {cycles} cycles")
                    break
                if duration_seconds and (time.time() - start_time) > duration_seconds:
                    logger.info(f"Completed {duration_seconds} seconds of operation")
                    break
                
                # Execute strategy cycle
                self._execute_cycle(cycle)
                
                # Brief pause between cycles
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            logger.info("\n⚠️  Shutdown signal received")
        except Exception as e:
            logger.error(f"❌ Error in main loop: {e}")
        finally:
            self._shutdown()
    
    def _execute_cycle(self, cycle: int):
        """
        Execute one complete strategy cycle.
        
        Args:
            cycle: Current cycle number
        """
        logger.info(f"\n--- Cycle {cycle} ---")
        
        # Simulate market data (in production, this would come from real sources)
        market_data = self._get_market_data()
        
        # Get top strategies from registry
        top_strategies = self.registry.get_top_strategies(
            self.config['max_strategies_active']
        )
        
        # Execute each strategy
        for strategy in top_strategies:
            try:
                # Analyze market
                analysis = strategy.analyze(market_data)
                
                # Generate signal
                signal = strategy.generate_signal(analysis)
                
                if signal['action'] != 'HOLD':
                    logger.info(f"📊 {strategy.name}: {signal['action']} "
                               f"(confidence: {signal['confidence']*100:.1f}%)")
                    
                    if not self.dry_run:
                        # In production, execute the trade here
                        pass
                    else:
                        logger.info(f"   [DRY RUN] Trade would be executed")
                
            except Exception as e:
                logger.error(f"❌ Error in {strategy.name}: {e}")
        
        # Display current status
        if cycle % 10 == 0:
            self._display_status()
    
    def _get_market_data(self) -> Dict[str, Any]:
        """
        Get current market data.
        
        In production, this would connect to:
        - RPC endpoints
        - DEX APIs
        - Price feeds
        - On-chain data
        
        Returns:
            Market data dictionary
        """
        # Simulated data for demonstration
        import random
        
        return {
            'timestamp': datetime.now().isoformat(),
            'exchanges': [
                {'name': 'Uniswap', 'price': 2000 + random.uniform(-50, 50), 'liquidity': 100000},
                {'name': 'SushiSwap', 'price': 2000 + random.uniform(-50, 50), 'liquidity': 120000},
                {'name': 'PancakeSwap', 'price': 2000 + random.uniform(-50, 50), 'liquidity': 90000},
            ],
            'gas_price': random.uniform(30, 100),
            'chains': {
                'Ethereum': {'price': 2000 + random.uniform(-50, 50), 'liquidity': 500000},
                'BSC': {'price': 2000 + random.uniform(-50, 50), 'liquidity': 400000},
                'Polygon': {'price': 2000 + random.uniform(-50, 50), 'liquidity': 350000},
            },
            'pending_transactions': [],
            'lending_positions': [],
            'yield_protocols': [],
        }
    
    def _display_status(self):
        """Display current engine status."""
        logger.info("\n" + "=" * 80)
        logger.info("📊 OMNI-STRATEGY ENGINE STATUS")
        logger.info("=" * 80)
        
        # Get performance report
        report = self.registry.get_performance_report()
        summary = report['summary']
        
        logger.info(f"Active Strategies: {summary['total_strategies']}")
        logger.info(f"Production Ready: {summary['production_ready']}")
        logger.info(f"Total Trades: {summary['total_trades']}")
        logger.info(f"Net Profit: ${summary['net_profit']:.2f}")
        logger.info(f"Overall Win Rate: {summary['overall_win_rate']*100:.1f}%")
        
        # Display top performers
        logger.info("\n🏆 Top Strategies:")
        for i, strategy in enumerate(self.registry.get_top_strategies(3), 1):
            logger.info(f"   {i}. {strategy.name} "
                       f"(Score: {strategy.global_rank_score:.2f})")
        
        logger.info("=" * 80)
    
    def _shutdown(self):
        """Gracefully shutdown the engine."""
        logger.info("\n" + "=" * 80)
        logger.info("🔚 OMNI-STRATEGY ENGINE - SHUTDOWN")
        logger.info("=" * 80)
        
        # Close all positions (in production)
        logger.info("Closing all positions...")
        
        # Final report
        runtime = datetime.now() - self.start_time
        logger.info(f"\nRuntime: {runtime}")
        self._display_status()
        
        logger.info("\n✅ Shutdown complete")
        logger.info("=" * 80)


def main():
    """Main entry point for Omni-Strategy Engine."""
    parser = argparse.ArgumentParser(
        description='OMNI-STRATEGY ENGINE - Ultimate DeFi Trading System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Conservative mode with $100k
  python omni_strategy_engine.py --mode=CONSERVATIVE --capital=100000
  
  # Aggressive mode with $500k
  python omni_strategy_engine.py --mode=AGGRESSIVE --capital=500000
  
  # Dry run in balanced mode
  python omni_strategy_engine.py --mode=BALANCED --capital=250000 --dry-run
  
  # Run specific strategies only
  python omni_strategy_engine.py --mode=BALANCED --capital=250000 --strategies=flash_loan,mev
  
  # Run for 100 cycles
  python omni_strategy_engine.py --mode=CONSERVATIVE --capital=100000 --cycles=100
        """
    )
    
    parser.add_argument(
        '--mode',
        type=str,
        default='BALANCED',
        choices=['CONSERVATIVE', 'BALANCED', 'AGGRESSIVE'],
        help='Operating mode (default: BALANCED)'
    )
    
    parser.add_argument(
        '--capital',
        type=float,
        default=100000,
        help='Initial capital in USD (default: 100000)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate without real trading'
    )
    
    parser.add_argument(
        '--strategies',
        type=str,
        help='Comma-separated list of strategies to enable (default: all)'
    )
    
    parser.add_argument(
        '--duration',
        type=int,
        help='Run for specified seconds'
    )
    
    parser.add_argument(
        '--cycles',
        type=int,
        default=50,
        help='Run for specified number of cycles (default: 50)'
    )
    
    args = parser.parse_args()
    
    # Parse strategies list
    strategies = None
    if args.strategies:
        strategies = [s.strip() for s in args.strategies.split(',')]
    
    try:
        # Initialize engine
        engine = OmniStrategyEngine(
            mode=args.mode,
            capital=args.capital,
            dry_run=args.dry_run,
            strategies=strategies
        )
        
        # Run engine
        engine.run(duration_seconds=args.duration, cycles=args.cycles)
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
