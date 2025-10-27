"""Profit Optimizer - Dynamic strategy optimization and profit maximization."""

from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ProfitOptimizer:
    """
    Advanced profit optimization system.
    
    Dynamically optimizes strategy parameters, selects best performing
    strategies, and maximizes overall profit generation.
    """
    
    def __init__(self):
        self.strategy_performance = {}
        self.optimization_history = []
        self.total_profit = 0
        self.total_trades = 0
        logger.info("Profit Optimizer initialized")
    
    def optimize_execution(self, 
                          market_analysis: Dict[str, Any],
                          available_strategies: List[str],
                          risk_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize trade execution for maximum profit.
        
        Args:
            market_analysis: Current market analysis
            available_strategies: List of available strategies
            risk_assessment: Risk assessment for the trade
            
        Returns:
            Optimization results with recommended strategy and parameters
        """
        # Select best strategy for current conditions
        best_strategy = self._select_optimal_strategy(
            market_analysis, 
            available_strategies
        )
        
        # Optimize entry and exit points
        entry_exit = self._optimize_entry_exit(market_analysis, risk_assessment)
        
        # Calculate expected profit
        expected_profit = self._calculate_expected_profit(
            market_analysis,
            risk_assessment,
            best_strategy
        )
        
        optimization = {
            'recommended_strategy': best_strategy,
            'entry_price': entry_exit['entry'],
            'exit_price': entry_exit['exit'],
            'expected_profit': expected_profit,
            'confidence': self._calculate_confidence(market_analysis, best_strategy),
            'execution_priority': self._calculate_priority(expected_profit, risk_assessment),
            'timestamp': datetime.now().isoformat()
        }
        
        return optimization
    
    def _select_optimal_strategy(self, 
                                 market_analysis: Dict[str, Any],
                                 available_strategies: List[str]) -> str:
        """Select the best strategy for current market conditions."""
        strategy_scores = {}
        
        for strategy in available_strategies:
            score = 0
            
            # Score based on market conditions
            if strategy == 'arbitrage':
                # Arbitrage works best with price differences
                opportunities = market_analysis.get('opportunities', [])
                arbitrage_ops = [op for op in opportunities if op.get('type') == 'arbitrage']
                score = len(arbitrage_ops) * 10
                
            elif strategy == 'trend_following':
                # Trend following works best with strong trends
                trend_strength = market_analysis.get('trend_strength', 0)
                score = trend_strength * 100
                
            elif strategy == 'mean_reversion':
                # Mean reversion works best with high deviation
                deviation = abs(market_analysis.get('price_deviation', 0))
                score = deviation * 20
                
            elif strategy == 'momentum':
                # Momentum works best with strong momentum
                momentum = abs(market_analysis.get('momentum', 0))
                score = momentum * 100
                
            elif strategy == 'liquidity_provision':
                # Liquidity provision works best with high liquidity
                liquidity = market_analysis.get('liquidity', 0)
                score = liquidity / 100000
            
            # Adjust score based on historical performance
            if strategy in self.strategy_performance:
                perf = self.strategy_performance[strategy]
                win_rate = perf.get('win_rate', 0.5)
                score *= win_rate
            
            strategy_scores[strategy] = score
        
        # Return strategy with highest score
        best_strategy = max(strategy_scores.items(), key=lambda x: x[1])[0]
        logger.info(f"Optimal strategy selected: {best_strategy} (score: {strategy_scores[best_strategy]:.2f})")
        
        return best_strategy
    
    def _optimize_entry_exit(self, 
                            market_analysis: Dict[str, Any],
                            risk_assessment: Dict[str, Any]) -> Dict[str, float]:
        """Optimize entry and exit price points."""
        current_price = market_analysis.get('price', 0)
        volatility = market_analysis.get('volatility', 0)
        trend = market_analysis.get('trend', 0)
        
        # Calculate optimal entry
        if trend > 0:
            # For uptrend, wait for slight pullback
            entry_adjustment = -volatility * 0.5
        elif trend < 0:
            # For downtrend, wait for slight bounce
            entry_adjustment = volatility * 0.5
        else:
            entry_adjustment = 0
        
        entry_price = current_price * (1 + entry_adjustment)
        
        # Calculate optimal exit based on risk assessment
        stop_loss = risk_assessment.get('stop_loss', 0.02)
        take_profit = risk_assessment.get('take_profit', 0.05)
        
        if trend > 0:
            exit_price = entry_price * (1 + take_profit)
        else:
            exit_price = entry_price * (1 - take_profit)
        
        return {
            'entry': entry_price,
            'exit': exit_price
        }
    
    def _calculate_expected_profit(self,
                                  market_analysis: Dict[str, Any],
                                  risk_assessment: Dict[str, Any],
                                  strategy: str) -> float:
        """Calculate expected profit for a trade."""
        position_size = risk_assessment.get('position_size', 0)
        take_profit = risk_assessment.get('take_profit', 0)
        
        # Get strategy win rate
        win_rate = 0.5  # Default
        if strategy in self.strategy_performance:
            win_rate = self.strategy_performance[strategy].get('win_rate', 0.5)
        
        # Expected value calculation
        expected_profit = position_size * take_profit * win_rate
        
        # Adjust for opportunities
        opportunities = market_analysis.get('opportunities', [])
        if opportunities:
            expected_profit *= (1 + len(opportunities) * 0.1)
        
        return expected_profit
    
    def _calculate_confidence(self, 
                             market_analysis: Dict[str, Any],
                             strategy: str) -> float:
        """Calculate confidence level for the trade."""
        confidence = 0.5  # Base confidence
        
        # Increase confidence with clear opportunities
        opportunities = market_analysis.get('opportunities', [])
        confidence += len(opportunities) * 0.1
        
        # Increase confidence with strong trend
        trend_strength = market_analysis.get('trend_strength', 0)
        confidence += trend_strength * 0.3
        
        # Adjust based on historical performance
        if strategy in self.strategy_performance:
            win_rate = self.strategy_performance[strategy].get('win_rate', 0.5)
            confidence *= win_rate
        
        return min(confidence, 1.0)
    
    def _calculate_priority(self,
                           expected_profit: float,
                           risk_assessment: Dict[str, Any]) -> str:
        """Calculate execution priority."""
        risk_reward = risk_assessment.get('risk_reward_ratio', 0)
        
        if expected_profit > 0.05 and risk_reward > 3:
            return "HIGH"
        elif expected_profit > 0.02 and risk_reward > 2:
            return "MEDIUM"
        else:
            return "LOW"
    
    def record_trade_result(self, 
                           strategy: str,
                           profit: float,
                           success: bool):
        """Record trade result for optimization."""
        if strategy not in self.strategy_performance:
            self.strategy_performance[strategy] = {
                'total_profit': 0,
                'trades': 0,
                'wins': 0,
                'losses': 0,
                'win_rate': 0
            }
        
        perf = self.strategy_performance[strategy]
        perf['total_profit'] += profit
        perf['trades'] += 1
        
        if success:
            perf['wins'] += 1
        else:
            perf['losses'] += 1
        
        perf['win_rate'] = perf['wins'] / perf['trades']
        
        self.total_profit += profit
        self.total_trades += 1
        
        logger.info(f"Trade result recorded: {strategy} - Profit: {profit:.4f} - Success: {success}")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report."""
        return {
            'total_profit': self.total_profit,
            'total_trades': self.total_trades,
            'average_profit_per_trade': self.total_profit / self.total_trades if self.total_trades > 0 else 0,
            'strategy_performance': self.strategy_performance,
            'best_strategy': self._get_best_strategy(),
            'overall_win_rate': self._calculate_overall_win_rate()
        }
    
    def _get_best_strategy(self) -> Optional[str]:
        """Identify best performing strategy."""
        if not self.strategy_performance:
            return None
        
        best_strategy = max(
            self.strategy_performance.items(),
            key=lambda x: x[1]['total_profit']
        )
        
        return best_strategy[0]
    
    def _calculate_overall_win_rate(self) -> float:
        """Calculate overall win rate across all strategies."""
        total_wins = sum(perf['wins'] for perf in self.strategy_performance.values())
        total_trades = sum(perf['trades'] for perf in self.strategy_performance.values())
        
        return total_wins / total_trades if total_trades > 0 else 0
