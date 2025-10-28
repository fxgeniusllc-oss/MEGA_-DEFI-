"""
Statistical Arbitrage Strategy
===============================

Advanced strategy using statistical models for mean-reversion arbitrage.
Targets 20-80% APY with low-risk statistical edge.
"""

from typing import Dict, Any, List
from .base_strategy import BaseStrategy
from ..config import Config
import logging

logger = logging.getLogger(__name__)


class StatisticalArbitrageStrategy(BaseStrategy):
    """
    Statistical arbitrage using correlation and co-integration analysis.
    
    This strategy:
    - Identifies correlated asset pairs
    - Detects mean-reversion opportunities
    - Uses z-score for entry/exit signals
    - Maintains market-neutral positions
    """
    
    def __init__(self,
                 z_score_threshold: float = 2.0,
                 correlation_threshold: float = 0.7,
                 lookback_period: int = 30):
        """
        Initialize Statistical Arbitrage Strategy.
        
        Args:
            z_score_threshold: Z-score threshold for entry signals
            correlation_threshold: Minimum correlation for pair selection
            lookback_period: Historical period for analysis (days)
        """
        super().__init__(
            name="Statistical Arbitrage",
            description="Advanced statistical arbitrage with mean-reversion"
        )
        
        self.z_score_threshold = z_score_threshold
        self.correlation_threshold = correlation_threshold
        self.lookback_period = lookback_period
        
        self.pairs_analyzed = 0
        self.mean_reversion_trades = 0
    
    def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze market for statistical arbitrage opportunities.
        
        Args:
            market_data: Market data with price history
            
        Returns:
            Analysis with stat arb opportunities
        """
        pairs = market_data.get('asset_pairs', [])
        price_history = market_data.get('price_history', {})
        
        if not pairs or not price_history:
            return {'opportunities': [], 'best_opportunity': None}
        
        opportunities = []
        
        for pair in pairs:
            asset_a = pair.get('asset_a')
            asset_b = pair.get('asset_b')
            
            # Get price histories
            prices_a = price_history.get(asset_a, [])
            prices_b = price_history.get(asset_b, [])
            
            if len(prices_a) < self.lookback_period or len(prices_b) < self.lookback_period:
                continue
            
            self.pairs_analyzed += 1
            
            # Calculate correlation
            correlation = self._calculate_correlation(prices_a, prices_b)
            
            if abs(correlation) < self.correlation_threshold:
                continue  # Not correlated enough
            
            # Calculate spread
            spread = self._calculate_spread(prices_a, prices_b)
            
            # Calculate z-score
            z_score = self._calculate_z_score(spread)
            
            # Check for entry signal
            if abs(z_score) >= self.z_score_threshold:
                opportunities.append({
                    'asset_a': asset_a,
                    'asset_b': asset_b,
                    'correlation': correlation,
                    'z_score': z_score,
                    'spread': spread[-1] if spread else 0,
                    'signal': 'LONG_A_SHORT_B' if z_score < 0 else 'SHORT_A_LONG_B',
                    'confidence': min(abs(z_score) / 3.0, 1.0),
                    'mean_reversion_score': self._calculate_mean_reversion_score(
                        z_score, correlation
                    ),
                })
        
        # Sort by mean reversion score
        opportunities.sort(key=lambda x: x['mean_reversion_score'], reverse=True)
        
        return {
            'opportunities': opportunities,
            'best_opportunity': opportunities[0] if opportunities else None,
            'total_opportunities': len(opportunities),
        }
    
    def _calculate_correlation(self, prices_a: List[float], prices_b: List[float]) -> float:
        """Calculate Pearson correlation coefficient."""
        n = min(len(prices_a), len(prices_b))
        if n < 2:
            return 0.0
        
        prices_a = prices_a[-n:]
        prices_b = prices_b[-n:]
        
        # Calculate means
        mean_a = sum(prices_a) / n
        mean_b = sum(prices_b) / n
        
        # Calculate correlation
        numerator = sum((prices_a[i] - mean_a) * (prices_b[i] - mean_b) for i in range(n))
        
        sum_sq_a = sum((prices_a[i] - mean_a) ** 2 for i in range(n))
        sum_sq_b = sum((prices_b[i] - mean_b) ** 2 for i in range(n))
        
        denominator = (sum_sq_a * sum_sq_b) ** 0.5
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    def _calculate_spread(self, prices_a: List[float], prices_b: List[float]) -> List[float]:
        """Calculate price spread between two assets."""
        n = min(len(prices_a), len(prices_b))
        return [prices_a[i] - prices_b[i] for i in range(n)]
    
    def _calculate_z_score(self, spread: List[float]) -> float:
        """Calculate z-score of current spread."""
        if len(spread) < 2:
            return 0.0
        
        mean = sum(spread) / len(spread)
        variance = sum((x - mean) ** 2 for x in spread) / len(spread)
        std_dev = variance ** 0.5
        
        if std_dev == 0:
            return 0.0
        
        current_spread = spread[-1]
        z_score = (current_spread - mean) / std_dev
        
        return z_score
    
    def _calculate_mean_reversion_score(self, z_score: float, correlation: float) -> float:
        """Calculate mean reversion opportunity score."""
        # Z-score component (weight: 60%)
        z_score_component = min(abs(z_score) / 3.0, 1.0) * 60
        
        # Correlation component (weight: 40%)
        correlation_component = abs(correlation) * 40
        
        return z_score_component + correlation_component
    
    def generate_signal(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate stat arb signal."""
        best_opp = analysis.get('best_opportunity')
        
        if not best_opp:
            return {
                'action': 'HOLD',
                'confidence': 0.0,
                'reason': 'No statistical arbitrage opportunities'
            }
        
        return {
            'action': 'EXECUTE_STAT_ARB',
            'confidence': best_opp['confidence'],
            'asset_a': best_opp['asset_a'],
            'asset_b': best_opp['asset_b'],
            'signal': best_opp['signal'],
            'z_score': best_opp['z_score'],
            'correlation': best_opp['correlation'],
            'expected_profit': min(abs(best_opp['z_score']) * 0.02, 0.1),  # 2% per z-score unit
        }
    
    def calculate_position_size(self,
                               signal: Dict[str, Any],
                               portfolio_value: float,
                               risk_params: Dict[str, Any]) -> float:
        """Calculate position size for stat arb."""
        if signal['action'] == 'HOLD':
            return 0.0
        
        z_score = abs(signal.get('z_score', 0))
        correlation = abs(signal.get('correlation', 0))
        
        max_position = risk_params.get('max_position_size', 0.2)
        
        # Scale with z-score and correlation strength
        optimal_size = min(
            max_position,
            (z_score / 3.0) * correlation * 0.3
        )
        
        return max(optimal_size, 0.02)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get strategy performance metrics."""
        metrics = super().get_performance_metrics()
        
        metrics.update({
            'pairs_analyzed': self.pairs_analyzed,
            'mean_reversion_trades': self.mean_reversion_trades,
        })
        
        return metrics
