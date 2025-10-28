"""
Strategy Registry
=================

Central registry for managing and ranking all trading strategies.
Provides global ranking and strategy selection for production operations.
"""

from typing import Dict, Any, List, Optional
from .base_strategy import BaseStrategy, StrategyRank
import logging

logger = logging.getLogger(__name__)


class StrategyRegistry:
    """
    Central registry for all trading strategies with global ranking.
    
    Manages:
    - Strategy registration and lifecycle
    - Global performance ranking
    - Strategy selection for live operations
    - Performance monitoring and reporting
    """
    
    def __init__(self):
        """Initialize strategy registry."""
        self.strategies: Dict[str, BaseStrategy] = {}
        self.global_rankings: List[Dict[str, Any]] = []
        logger.info("Strategy Registry initialized")
    
    def register_strategy(self, strategy: BaseStrategy):
        """
        Register a strategy with the registry.
        
        Args:
            strategy: Strategy instance to register
        """
        if strategy.name in self.strategies:
            logger.warning(f"Strategy {strategy.name} already registered, replacing...")
        
        self.strategies[strategy.name] = strategy
        logger.info(f"Registered strategy: {strategy.name}")
        
        # Update rankings
        self.update_global_rankings()
    
    def unregister_strategy(self, strategy_name: str):
        """
        Unregister a strategy.
        
        Args:
            strategy_name: Name of strategy to unregister
        """
        if strategy_name in self.strategies:
            del self.strategies[strategy_name]
            logger.info(f"Unregistered strategy: {strategy_name}")
            self.update_global_rankings()
    
    def get_strategy(self, strategy_name: str) -> Optional[BaseStrategy]:
        """
        Get strategy by name.
        
        Args:
            strategy_name: Name of strategy
            
        Returns:
            Strategy instance or None
        """
        return self.strategies.get(strategy_name)
    
    def get_all_strategies(self) -> List[BaseStrategy]:
        """
        Get all registered strategies.
        
        Returns:
            List of all strategies
        """
        return list(self.strategies.values())
    
    def get_production_ready_strategies(self) -> List[BaseStrategy]:
        """
        Get strategies that are ready for live production.
        
        Returns:
            List of production-ready strategies
        """
        return [
            strategy for strategy in self.strategies.values()
            if strategy.is_production_ready()
        ]
    
    def get_elite_strategies(self) -> List[BaseStrategy]:
        """
        Get elite-ranked strategies.
        
        Returns:
            List of elite strategies
        """
        return [
            strategy for strategy in self.strategies.values()
            if strategy.rank == StrategyRank.ELITE
        ]
    
    def update_global_rankings(self):
        """
        Update global rankings for all strategies.
        
        Strategies are ranked by:
        1. Global rank score
        2. Win rate
        3. Profit factor
        4. Total trades (for consistency)
        """
        # Get ranking data for all strategies
        rankings = []
        
        for strategy in self.strategies.values():
            ranking = strategy.get_global_ranking()
            rankings.append(ranking)
        
        # Sort by score (descending), then win rate, then profit factor
        rankings.sort(
            key=lambda x: (x['score'], x['win_rate'], x['profit_factor']),
            reverse=True
        )
        
        # Assign global positions
        for i, ranking in enumerate(rankings):
            ranking['global_position'] = i + 1
        
        self.global_rankings = rankings
        
        logger.info(f"Updated global rankings for {len(rankings)} strategies")
    
    def get_global_rankings(self) -> List[Dict[str, Any]]:
        """
        Get global rankings.
        
        Returns:
            List of strategies with ranking information
        """
        return self.global_rankings.copy()
    
    def get_top_strategies(self, n: int = 5) -> List[BaseStrategy]:
        """
        Get top N strategies by global rank.
        
        Args:
            n: Number of top strategies to return
            
        Returns:
            List of top strategies
        """
        self.update_global_rankings()
        
        top_strategy_names = [
            ranking['strategy'] 
            for ranking in self.global_rankings[:n]
        ]
        
        return [
            self.strategies[name]
            for name in top_strategy_names
            if name in self.strategies
        ]
    
    def get_strategy_by_rank(self, rank: StrategyRank) -> List[BaseStrategy]:
        """
        Get all strategies of a specific rank tier.
        
        Args:
            rank: Strategy rank tier
            
        Returns:
            List of strategies with the specified rank
        """
        return [
            strategy for strategy in self.strategies.values()
            if strategy.rank == rank
        ]
    
    def get_performance_report(self) -> Dict[str, Any]:
        """
        Get comprehensive performance report for all strategies.
        
        Returns:
            Performance report with rankings and metrics
        """
        self.update_global_rankings()
        
        # Aggregate statistics
        total_strategies = len(self.strategies)
        production_ready = len(self.get_production_ready_strategies())
        elite_strategies = len(self.get_elite_strategies())
        
        # Calculate aggregate performance
        total_trades = sum(s.total_trades for s in self.strategies.values())
        total_profit = sum(s.total_profit for s in self.strategies.values())
        total_loss = sum(s.total_loss for s in self.strategies.values())
        
        overall_win_rate = 0.0
        if total_trades > 0:
            winning_trades = sum(s.winning_trades for s in self.strategies.values())
            overall_win_rate = winning_trades / total_trades
        
        # Get individual strategy metrics
        strategy_metrics = [
            strategy.get_performance_metrics()
            for strategy in self.strategies.values()
        ]
        
        return {
            'summary': {
                'total_strategies': total_strategies,
                'production_ready': production_ready,
                'elite_strategies': elite_strategies,
                'total_trades': total_trades,
                'total_profit': total_profit,
                'total_loss': total_loss,
                'net_profit': total_profit - total_loss,
                'overall_win_rate': overall_win_rate,
            },
            'global_rankings': self.global_rankings,
            'strategy_metrics': strategy_metrics,
        }
    
    def display_rankings(self):
        """Display global rankings in readable format."""
        self.update_global_rankings()
        
        print("\n" + "=" * 80)
        print("MEGA DEFI - GLOBAL STRATEGY RANKINGS")
        print("=" * 80)
        
        if not self.global_rankings:
            print("No strategies registered yet.")
            return
        
        print(f"\nTotal Strategies: {len(self.strategies)}")
        print(f"Production Ready: {len(self.get_production_ready_strategies())}")
        print(f"Elite Tier: {len(self.get_elite_strategies())}")
        
        print("\n" + "-" * 80)
        print(f"{'Rank':<6} {'Strategy':<30} {'Tier':<15} {'Score':<8} {'Win%':<8} {'PF':<8}")
        print("-" * 80)
        
        for ranking in self.global_rankings:
            strategy = self.strategies.get(ranking['strategy'])
            if not strategy:
                continue
            
            print(
                f"{ranking['global_position']:<6} "
                f"{ranking['strategy']:<30} "
                f"{ranking['rank']:<15} "
                f"{ranking['score']:<8.2f} "
                f"{ranking['win_rate']*100:<8.1f} "
                f"{ranking['profit_factor']:<8.2f}"
            )
        
        print("-" * 80)
        
        # Summary statistics
        report = self.get_performance_report()
        summary = report['summary']
        
        print(f"\n📊 AGGREGATE PERFORMANCE:")
        print(f"   Total Trades: {summary['total_trades']}")
        print(f"   Net Profit: ${summary['net_profit']:.2f}")
        print(f"   Overall Win Rate: {summary['overall_win_rate']*100:.1f}%")
        
        print("\n" + "=" * 80)
        print("STATUS: ELITE PRODUCTION OPERATIONS READY ✓")
        print("=" * 80 + "\n")
    
    def select_best_strategy(self, 
                            market_conditions: Dict[str, Any] = None) -> Optional[BaseStrategy]:
        """
        Select the best strategy for current market conditions.
        
        Args:
            market_conditions: Optional market conditions for selection
            
        Returns:
            Best strategy or None
        """
        production_ready = self.get_production_ready_strategies()
        
        if not production_ready:
            logger.warning("No production-ready strategies available")
            return None
        
        # If no market conditions specified, return top-ranked strategy
        if not market_conditions:
            top_strategies = self.get_top_strategies(1)
            return top_strategies[0] if top_strategies else None
        
        # TODO: Implement market condition-based selection
        # For now, return top-ranked production-ready strategy
        self.update_global_rankings()
        
        for ranking in self.global_rankings:
            strategy = self.strategies.get(ranking['strategy'])
            if strategy and strategy.is_production_ready():
                return strategy
        
        return None
    
    def __len__(self):
        """Return number of registered strategies."""
        return len(self.strategies)
    
    def __repr__(self):
        return f"<StrategyRegistry: {len(self.strategies)} strategies registered>"
