"""
MEGA DeFi Profit Machine - Main Orchestrator
============================================

The unstoppable profit machine that combines vision with technical expertise.
"""

import logging
from typing import Dict, Any, Optional
from .core.strategy_engine import StrategyEngine, StrategyType, Signal
from .core.market_analyzer import MarketAnalyzer
from .core.risk_manager import RiskManager
from .core.profit_optimizer import ProfitOptimizer
from .config import Config

# Configure logging from environment variables
log_level = getattr(logging, Config.get_log_level(), logging.INFO)
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class ProfitMachine:
    """
    The MEGA DeFi Profit Machine - An unstoppable profit generation system.
    
    This machine combines:
    - Strategic Vision: Advanced market analysis and opportunity identification
    - Technical Expertise: Multiple algorithmic strategies and risk management
    - Profit Optimization: Dynamic parameter tuning and strategy selection
    """
    
    def __init__(self, 
                 portfolio_value: Optional[float] = None,
                 max_risk_per_trade: Optional[float] = None,
                 max_position_size: Optional[float] = None,
                 enable_ml: bool = False,
                 enable_data_sources: bool = False):
        """
        Initialize the Profit Machine.
        
        Args:
            portfolio_value: Starting portfolio value in USD (defaults to config)
            max_risk_per_trade: Maximum risk per trade (defaults to config)
            max_position_size: Maximum position size (defaults to config)
            enable_ml: Enable ML components (optional, experimental)
            enable_data_sources: Enable data source integrations (optional, experimental)
        """
        logger.info("=" * 60)
        logger.info("INITIALIZING MEGA DEFI PROFIT MACHINE")
        logger.info("=" * 60)
        
        # Load configuration from environment variables if not provided
        if portfolio_value is None:
            portfolio_value = Config.get_initial_portfolio_value()
        if max_risk_per_trade is None:
            max_risk_per_trade = Config.get_max_risk_per_trade()
        if max_position_size is None:
            max_position_size = Config.get_max_position_size()
        
        logger.info(f"Configuration loaded from environment")
        logger.info(f"Environment: {Config.get_environment()}")
        logger.info(f"Debug Mode: {Config.get_debug_mode()}")
        logger.info(f"Dry Run: {Config.get_dry_run()}")
        
        self.strategy_engine = StrategyEngine()
        self.market_analyzer = MarketAnalyzer()
        self.risk_manager = RiskManager(max_risk_per_trade, max_position_size)
        self.profit_optimizer = ProfitOptimizer()
        
        # Optional: Initialize intelligence layer
        self.intelligence_layer = None
        if enable_ml or enable_data_sources:
            try:
                from .core.intelligence_layer import IntelligenceLayer
                self.intelligence_layer = IntelligenceLayer(
                    enable_ml=enable_ml,
                    enable_data_sources=enable_data_sources
                )
                logger.info("🧠 Intelligence Layer activated (ML & Data Sources)")
            except ImportError as e:
                logger.warning(f"Could not initialize intelligence layer: {e}")
        
        self.risk_manager.update_portfolio(portfolio_value)
        
        # Register default strategies
        self._register_default_strategies()
        
        logger.info(f"Portfolio Value: ${portfolio_value:,.2f}")
        logger.info(f"Max Risk Per Trade: {max_risk_per_trade*100:.1f}%")
        logger.info(f"Max Position Size: {max_position_size*100:.1f}%")
        logger.info("Profit Machine Ready - UNSTOPPABLE MODE ACTIVATED")
        logger.info("=" * 60)
    
    def _register_default_strategies(self):
        """Register all available trading strategies."""
        strategies = [
            (StrategyType.ARBITRAGE, {'threshold': 0.01}),
            (StrategyType.TREND_FOLLOWING, {'min_strength': 0.5}),
            (StrategyType.MEAN_REVERSION, {'deviation_threshold': 2.0}),
            (StrategyType.MOMENTUM, {'momentum_threshold': 0.05}),
            (StrategyType.LIQUIDITY_PROVISION, {'min_fee_rate': 0.003}),
        ]
        
        for strategy_type, params in strategies:
            self.strategy_engine.register_strategy(strategy_type, params)
    
    def process_market_data(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process market data and generate trading signals.
        
        Args:
            market_data: Current market data (price, volume, liquidity, etc.)
            
        Returns:
            Trading recommendation with strategy, signals, and risk assessment
        """
        logger.info("Processing market data...")
        
        # Analyze market
        analysis = self.market_analyzer.analyze_market(market_data)
        logger.info(f"Market Analysis: Trend={analysis['trend']:.4f}, "
                   f"Volatility={analysis['volatility']:.4f}, "
                   f"Opportunities={len(analysis['opportunities'])}")
        
        # Get available strategies
        available_strategies = list(self.strategy_engine.active_strategies.keys())
        
        # Optimize execution
        optimization = self.profit_optimizer.optimize_execution(
            analysis,
            available_strategies,
            {'position_size': self.risk_manager.max_position_size}
        )
        
        # Get recommended strategy
        strategy_type = StrategyType(optimization['recommended_strategy'])
        
        # Execute strategy
        signal = self.strategy_engine.execute_strategy(strategy_type, analysis)
        
        # Assess risk
        risk_assessment = self.risk_manager.assess_risk(analysis, strategy_type.value)
        
        # Compile recommendation
        recommendation = {
            'signal': signal.value,
            'strategy': strategy_type.value,
            'confidence': optimization['confidence'],
            'expected_profit': optimization['expected_profit'],
            'risk_assessment': risk_assessment,
            'market_analysis': analysis,
            'optimization': optimization,
            'approved': risk_assessment['approved'] and signal != Signal.HOLD
        }
        
        if recommendation['approved']:
            logger.info(f"✓ TRADE APPROVED: {signal.value.upper()} via {strategy_type.value}")
            logger.info(f"  Expected Profit: {optimization['expected_profit']:.2%}")
            logger.info(f"  Confidence: {optimization['confidence']:.2%}")
            logger.info(f"  Risk/Reward: {risk_assessment['risk_reward_ratio']:.2f}")
        else:
            logger.info(f"✗ Trade not approved: {signal.value}")
        
        return recommendation
    
    def execute_trade(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a trade based on recommendation.
        
        Args:
            recommendation: Trading recommendation from process_market_data
            
        Returns:
            Trade execution result
        """
        if not recommendation['approved']:
            return {
                'executed': False,
                'reason': 'Trade not approved by risk management'
            }
        
        strategy = recommendation['strategy']
        signal = recommendation['signal']
        risk_assessment = recommendation['risk_assessment']
        
        # Simulate trade execution
        position_size = risk_assessment['position_size']
        entry_price = recommendation['optimization']['entry_price']
        
        position_id = f"{strategy}_{signal}_{entry_price}"
        
        self.risk_manager.open_position(position_id, {
            'strategy': strategy,
            'signal': signal,
            'size': position_size,
            'entry_price': entry_price,
            'stop_loss': risk_assessment['stop_loss'],
            'take_profit': risk_assessment['take_profit']
        })
        
        logger.info(f"Trade Executed: {signal.upper()} {position_size:.2%} of portfolio")
        
        return {
            'executed': True,
            'position_id': position_id,
            'strategy': strategy,
            'signal': signal,
            'position_size': position_size,
            'entry_price': entry_price,
            'stop_loss': risk_assessment['stop_loss'],
            'take_profit': risk_assessment['take_profit']
        }
    
    def close_trade(self, 
                   position_id: str,
                   exit_price: float,
                   profit: float,
                   success: bool):
        """
        Close a trade and record results.
        
        Args:
            position_id: ID of the position to close
            exit_price: Exit price
            profit: Profit/loss from the trade
            success: Whether the trade was successful
        """
        if position_id in self.risk_manager.active_positions:
            position = self.risk_manager.active_positions[position_id]
            strategy = position['strategy']
            
            # Record trade result
            self.profit_optimizer.record_trade_result(strategy, profit, success)
            
            # Close position
            self.risk_manager.close_position(position_id)
            
            logger.info(f"Trade Closed: Profit={profit:.4f} ({'WIN' if success else 'LOSS'})")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report."""
        return {
            'portfolio_status': self.risk_manager.get_portfolio_status(),
            'market_summary': self.market_analyzer.get_market_summary(),
            'profit_report': self.profit_optimizer.get_performance_report()
        }
    
    def display_performance(self):
        """Display performance report in readable format."""
        report = self.get_performance_report()
        
        print("\n" + "=" * 60)
        print("MEGA DEFI PROFIT MACHINE - PERFORMANCE REPORT")
        print("=" * 60)
        
        # Portfolio Status
        portfolio = report['portfolio_status']
        print("\n📊 PORTFOLIO STATUS:")
        print(f"  Value: ${portfolio['portfolio_value']:,.2f}")
        print(f"  Active Positions: {portfolio['active_positions']}")
        print(f"  Total Exposure: {portfolio['total_exposure']:.2%}")
        print(f"  Available Capacity: {portfolio['available_capacity']:.2%}")
        
        # Profit Report
        profit = report['profit_report']
        print("\n💰 PROFIT REPORT:")
        print(f"  Total Profit: ${profit['total_profit']:,.2f}")
        print(f"  Total Trades: {profit['total_trades']}")
        print(f"  Average Profit/Trade: ${profit['average_profit_per_trade']:,.4f}")
        print(f"  Overall Win Rate: {profit['overall_win_rate']:.2%}")
        if profit['best_strategy']:
            print(f"  Best Strategy: {profit['best_strategy']}")
        
        # Market Summary
        market = report['market_summary']
        if 'current_price' in market:
            print("\n📈 MARKET SUMMARY:")
            print(f"  Current Price: ${market['current_price']:,.2f}")
            print(f"  24h Change: {market['price_change_24h']:.2f}%")
            print(f"  Data Points: {market['data_points']}")
        
        print("\n" + "=" * 60)
        print("STATUS: UNSTOPPABLE ✓")
        print("=" * 60 + "\n")


def create_profit_machine(**kwargs) -> ProfitMachine:
    """
    Create and initialize a new Profit Machine instance.
    
    Args:
        **kwargs: Configuration parameters for ProfitMachine
        
    Returns:
        Initialized ProfitMachine instance
    """
    return ProfitMachine(**kwargs)
