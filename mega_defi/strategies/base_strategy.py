"""
Base Strategy Interface
=======================

Provides the foundation for all production-ready trading strategies with
global ranking capabilities for elite production operations.
"""

from typing import Dict, Any, List, Optional
from enum import Enum
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class StrategyRank(Enum):
    """Global ranking tiers for production strategies."""
    ELITE = "elite"           # Top 1% - highest profit/risk ratio
    ADVANCED = "advanced"     # Top 5% - excellent performance
    PROFESSIONAL = "professional"  # Top 20% - solid performance
    STANDARD = "standard"     # Standard performance
    EXPERIMENTAL = "experimental"  # Testing phase


class BaseStrategy(ABC):
    """
    Base class for all production-ready trading strategies.
    
    All strategies must implement:
    - analyze(): Analyze market conditions
    - generate_signal(): Generate trading signals
    - calculate_position_size(): Position sizing logic
    - get_performance_metrics(): Return performance data
    """
    
    def __init__(self, name: str, description: str):
        """
        Initialize base strategy.
        
        Args:
            name: Strategy name
            description: Strategy description
        """
        self.name = name
        self.description = description
        self.rank = StrategyRank.STANDARD
        self.enabled = True
        
        # Performance tracking
        self.total_trades = 0
        self.winning_trades = 0
        self.total_profit = 0.0
        self.total_loss = 0.0
        self.sharpe_ratio = 0.0
        self.max_drawdown = 0.0
        
        # Global ranking metrics
        self.global_rank_score = 0.0
        self.profit_factor = 0.0
        self.win_rate = 0.0
        self.average_profit = 0.0
        self.risk_adjusted_return = 0.0
        
        logger.info(f"Strategy initialized: {self.name}")
    
    @abstractmethod
    def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze market conditions and opportunities.
        
        Args:
            market_data: Current market data
            
        Returns:
            Analysis results with opportunities and signals
        """
        pass
    
    @abstractmethod
    def generate_signal(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate trading signal based on analysis.
        
        Args:
            analysis: Analysis results from analyze()
            
        Returns:
            Trading signal with confidence, direction, and parameters
        """
        pass
    
    @abstractmethod
    def calculate_position_size(self, 
                               signal: Dict[str, Any],
                               portfolio_value: float,
                               risk_params: Dict[str, Any]) -> float:
        """
        Calculate appropriate position size.
        
        Args:
            signal: Trading signal
            portfolio_value: Current portfolio value
            risk_params: Risk management parameters
            
        Returns:
            Position size as fraction of portfolio
        """
        pass
    
    def record_trade(self, profit: float, success: bool):
        """
        Record trade result and update metrics.
        
        Args:
            profit: Profit/loss from trade
            success: Whether trade was successful
        """
        self.total_trades += 1
        
        if success:
            self.winning_trades += 1
            self.total_profit += profit
        else:
            self.total_loss += abs(profit)
        
        # Update metrics
        self._update_metrics()
        
        logger.info(f"{self.name} - Trade recorded: Profit={profit:.4f}, Success={success}")
    
    def _update_metrics(self):
        """Update strategy performance metrics."""
        if self.total_trades > 0:
            self.win_rate = self.winning_trades / self.total_trades
            self.average_profit = (self.total_profit - self.total_loss) / self.total_trades
            
            if self.total_loss > 0:
                self.profit_factor = self.total_profit / self.total_loss
            else:
                self.profit_factor = float('inf') if self.total_profit > 0 else 0
            
            # Calculate risk-adjusted return (simplified Sharpe-like metric)
            if self.total_trades >= 10:
                returns = self.total_profit - self.total_loss
                risk = max(self.total_loss, 0.01)  # Avoid division by zero
                self.risk_adjusted_return = returns / risk
            
            # Update global rank score (weighted composite)
            self._calculate_global_rank_score()
    
    def _calculate_global_rank_score(self):
        """
        Calculate global ranking score based on multiple factors.
        
        Scoring factors:
        - Win rate (30%)
        - Profit factor (30%)
        - Risk-adjusted return (25%)
        - Total trades (consistency) (15%)
        """
        if self.total_trades < 5:
            self.global_rank_score = 0
            return
        
        # Normalize components (0-100 scale)
        win_rate_score = min(self.win_rate * 100, 100)
        profit_factor_score = min((self.profit_factor / 3.0) * 100, 100)
        risk_adjusted_score = min(self.risk_adjusted_return * 10, 100)
        consistency_score = min((self.total_trades / 100) * 100, 100)
        
        # Weighted average
        self.global_rank_score = (
            win_rate_score * 0.30 +
            profit_factor_score * 0.30 +
            risk_adjusted_score * 0.25 +
            consistency_score * 0.15
        )
        
        # Update rank tier
        if self.global_rank_score >= 90:
            self.rank = StrategyRank.ELITE
        elif self.global_rank_score >= 75:
            self.rank = StrategyRank.ADVANCED
        elif self.global_rank_score >= 60:
            self.rank = StrategyRank.PROFESSIONAL
        else:
            self.rank = StrategyRank.STANDARD
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive performance metrics.
        
        Returns:
            Dictionary with all performance data
        """
        return {
            'name': self.name,
            'description': self.description,
            'rank': self.rank.value,
            'global_rank_score': self.global_rank_score,
            'enabled': self.enabled,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'win_rate': self.win_rate,
            'total_profit': self.total_profit,
            'total_loss': self.total_loss,
            'average_profit': self.average_profit,
            'profit_factor': self.profit_factor,
            'risk_adjusted_return': self.risk_adjusted_return,
            'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown': self.max_drawdown,
        }
    
    def get_global_ranking(self) -> Dict[str, Any]:
        """
        Get global ranking information.
        
        Returns:
            Dictionary with ranking data
        """
        return {
            'strategy': self.name,
            'rank': self.rank.value,
            'score': self.global_rank_score,
            'win_rate': self.win_rate,
            'profit_factor': self.profit_factor,
            'risk_adjusted_return': self.risk_adjusted_return,
            'total_trades': self.total_trades,
        }
    
    def is_production_ready(self) -> bool:
        """
        Check if strategy is ready for live production.
        
        Returns:
            True if strategy meets production criteria
        """
        return (
            self.enabled and
            self.total_trades >= 10 and
            self.win_rate >= 0.5 and
            self.profit_factor >= 1.5 and
            self.global_rank_score >= 60
        )
    
    def __repr__(self):
        return f"<{self.name} (Rank: {self.rank.value}, Score: {self.global_rank_score:.2f})>"
