"""Strategy Engine - Core trading strategy execution system."""

from typing import Dict, List, Any, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class StrategyType(Enum):
    """Available trading strategy types."""
    ARBITRAGE = "arbitrage"
    TREND_FOLLOWING = "trend_following"
    MEAN_REVERSION = "mean_reversion"
    MOMENTUM = "momentum"
    LIQUIDITY_PROVISION = "liquidity_provision"


class Signal(Enum):
    """Trading signals."""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


class StrategyEngine:
    """
    Core strategy engine that orchestrates multiple trading strategies.
    
    This engine combines multiple proven DeFi strategies to maximize
    profit opportunities while managing risk.
    """
    
    def __init__(self):
        self.active_strategies = {}
        self.performance_metrics = {}
        logger.info("Strategy Engine initialized")
    
    def register_strategy(self, strategy_type: StrategyType, params: Dict[str, Any]):
        """
        Register a trading strategy with the engine.
        
        Args:
            strategy_type: Type of strategy to register
            params: Strategy-specific parameters
        """
        self.active_strategies[strategy_type.value] = {
            'type': strategy_type,
            'params': params,
            'enabled': True,
            'performance': {'total_profit': 0, 'trades': 0, 'win_rate': 0}
        }
        logger.info(f"Registered strategy: {strategy_type.value}")
    
    def execute_strategy(self, strategy_type: StrategyType, market_data: Dict[str, Any]) -> Signal:
        """
        Execute a specific strategy against market data.
        
        Args:
            strategy_type: Strategy to execute
            market_data: Current market conditions
            
        Returns:
            Trading signal (BUY, SELL, or HOLD)
        """
        if strategy_type.value not in self.active_strategies:
            logger.warning(f"Strategy {strategy_type.value} not registered")
            return Signal.HOLD
        
        strategy = self.active_strategies[strategy_type.value]
        if not strategy['enabled']:
            return Signal.HOLD
        
        # Execute strategy logic based on type
        if strategy_type == StrategyType.ARBITRAGE:
            return self._execute_arbitrage(market_data, strategy['params'])
        elif strategy_type == StrategyType.TREND_FOLLOWING:
            return self._execute_trend_following(market_data, strategy['params'])
        elif strategy_type == StrategyType.MEAN_REVERSION:
            return self._execute_mean_reversion(market_data, strategy['params'])
        elif strategy_type == StrategyType.MOMENTUM:
            return self._execute_momentum(market_data, strategy['params'])
        elif strategy_type == StrategyType.LIQUIDITY_PROVISION:
            return self._execute_liquidity_provision(market_data, strategy['params'])
        
        return Signal.HOLD
    
    def _execute_arbitrage(self, market_data: Dict[str, Any], params: Dict[str, Any]) -> Signal:
        """Execute arbitrage strategy."""
        price_diff = market_data.get('price_difference', 0)
        threshold = params.get('threshold', 0.01)
        
        if price_diff > threshold:
            return Signal.BUY
        elif price_diff < -threshold:
            return Signal.SELL
        return Signal.HOLD
    
    def _execute_trend_following(self, market_data: Dict[str, Any], params: Dict[str, Any]) -> Signal:
        """Execute trend-following strategy."""
        trend = market_data.get('trend', 0)
        strength = market_data.get('trend_strength', 0)
        min_strength = params.get('min_strength', 0.5)
        
        if trend > 0 and strength > min_strength:
            return Signal.BUY
        elif trend < 0 and strength > min_strength:
            return Signal.SELL
        return Signal.HOLD
    
    def _execute_mean_reversion(self, market_data: Dict[str, Any], params: Dict[str, Any]) -> Signal:
        """Execute mean reversion strategy."""
        deviation = market_data.get('price_deviation', 0)
        threshold = params.get('deviation_threshold', 2.0)
        
        if deviation > threshold:
            return Signal.SELL
        elif deviation < -threshold:
            return Signal.BUY
        return Signal.HOLD
    
    def _execute_momentum(self, market_data: Dict[str, Any], params: Dict[str, Any]) -> Signal:
        """Execute momentum strategy."""
        momentum = market_data.get('momentum', 0)
        threshold = params.get('momentum_threshold', 0.05)
        
        if momentum > threshold:
            return Signal.BUY
        elif momentum < -threshold:
            return Signal.SELL
        return Signal.HOLD
    
    def _execute_liquidity_provision(self, market_data: Dict[str, Any], params: Dict[str, Any]) -> Signal:
        """Execute liquidity provision strategy."""
        liquidity = market_data.get('liquidity', 0)
        fee_rate = market_data.get('fee_rate', 0)
        min_fee = params.get('min_fee_rate', 0.003)
        
        if fee_rate > min_fee and liquidity > 0:
            return Signal.BUY
        return Signal.HOLD
    
    def get_strategy_performance(self, strategy_type: StrategyType) -> Dict[str, Any]:
        """Get performance metrics for a strategy."""
        if strategy_type.value in self.active_strategies:
            return self.active_strategies[strategy_type.value]['performance']
        return {}
    
    def optimize_strategies(self):
        """Optimize strategy parameters based on performance."""
        logger.info("Optimizing strategy parameters...")
        for strategy_name, strategy in self.active_strategies.items():
            performance = strategy['performance']
            if performance['trades'] > 10:
                win_rate = performance['win_rate']
                if win_rate < 0.4:
                    strategy['enabled'] = False
                    logger.info(f"Disabled underperforming strategy: {strategy_name}")
