"""
MEGA DeFi Strategies Module
============================

Advanced production-ready trading strategies with global ranking capabilities.
"""

from .base_strategy import BaseStrategy, StrategyRank
from .flash_loan_arbitrage import FlashLoanArbitrageStrategy
from .cross_chain_arbitrage import CrossChainArbitrageStrategy
from .liquidation_hunter import LiquidationHunterStrategy
from .mev_strategy import MEVStrategy
from .statistical_arbitrage import StatisticalArbitrageStrategy
from .yield_optimizer import YieldOptimizerStrategy
from .strategy_registry import StrategyRegistry

__all__ = [
    'BaseStrategy',
    'StrategyRank',
    'FlashLoanArbitrageStrategy',
    'CrossChainArbitrageStrategy',
    'LiquidationHunterStrategy',
    'MEVStrategy',
    'StatisticalArbitrageStrategy',
    'YieldOptimizerStrategy',
    'StrategyRegistry',
]
