"""
MEGA DeFi Profit Machine
========================

An unstoppable profit-generating system that combines strategic vision 
with cutting-edge technical expertise in decentralized finance.

Core Components:
- Trading Strategy Engine: Multiple algorithmic trading strategies
- Market Analysis: Real-time market data processing and pattern recognition
- Risk Management: Advanced portfolio protection and position sizing
- Profit Optimization: Dynamic strategy selection and parameter tuning
"""

__version__ = "1.0.0"
__author__ = "FX Genius LLC"

from .core.strategy_engine import StrategyEngine
from .core.market_analyzer import MarketAnalyzer
from .core.risk_manager import RiskManager
from .core.profit_optimizer import ProfitOptimizer

__all__ = [
    'StrategyEngine',
    'MarketAnalyzer',
    'RiskManager',
    'ProfitOptimizer',
]
