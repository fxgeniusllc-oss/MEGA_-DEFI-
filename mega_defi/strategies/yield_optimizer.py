"""
Yield Optimizer Strategy
=========================

Advanced yield farming optimization strategy.
Targets 30-150% APY by dynamically allocating capital to highest-yield opportunities.
"""

from typing import Dict, Any, List
from .base_strategy import BaseStrategy
from ..config import Config
import logging

logger = logging.getLogger(__name__)


class YieldOptimizerStrategy(BaseStrategy):
    """
    Yield farming optimizer with dynamic allocation.
    
    This strategy:
    - Monitors yields across multiple protocols
    - Calculates risk-adjusted returns
    - Optimizes capital allocation
    - Auto-compounds rewards
    """
    
    def __init__(self,
                 min_apy: float = 0.15,
                 max_protocol_risk: float = 0.5,
                 rebalance_threshold: float = 0.05):
        """
        Initialize Yield Optimizer Strategy.
        
        Args:
            min_apy: Minimum acceptable APY (default 15%)
            max_protocol_risk: Maximum risk score (0-1)
            rebalance_threshold: Minimum APY difference for rebalancing
        """
        super().__init__(
            name="Yield Optimizer",
            description="Advanced yield farming optimization"
        )
        
        self.min_apy = min_apy
        self.max_protocol_risk = max_protocol_risk
        self.rebalance_threshold = rebalance_threshold
        
        self.protocols_monitored = 0
        self.rebalances_executed = 0
        self.total_yield_earned = 0.0
    
    def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze yield farming opportunities.
        
        Args:
            market_data: Market data with protocol yields
            
        Returns:
            Analysis with yield opportunities
        """
        protocols = market_data.get('yield_protocols', [])
        current_allocation = market_data.get('current_allocation', {})
        
        if not protocols:
            return {'opportunities': [], 'best_opportunity': None}
        
        self.protocols_monitored += len(protocols)
        
        opportunities = []
        
        for protocol in protocols:
            protocol_name = protocol.get('name')
            apy = protocol.get('apy', 0)
            tvl = protocol.get('tvl', 0)
            risk_score = protocol.get('risk_score', 0.5)
            
            # Filter by minimum requirements
            if apy < self.min_apy or risk_score > self.max_protocol_risk:
                continue
            
            # Calculate risk-adjusted yield
            risk_adjusted_apy = self._calculate_risk_adjusted_yield(apy, risk_score, tvl)
            
            # Calculate opportunity score
            opportunity_score = self._calculate_opportunity_score(
                risk_adjusted_apy, tvl, risk_score
            )
            
            opportunities.append({
                'protocol': protocol_name,
                'apy': apy,
                'risk_adjusted_apy': risk_adjusted_apy,
                'tvl': tvl,
                'risk_score': risk_score,
                'opportunity_score': opportunity_score,
                'current_allocation': current_allocation.get(protocol_name, 0),
            })
        
        # Sort by opportunity score
        opportunities.sort(key=lambda x: x['opportunity_score'], reverse=True)
        
        return {
            'opportunities': opportunities,
            'best_opportunity': opportunities[0] if opportunities else None,
            'total_opportunities': len(opportunities),
        }
    
    def _calculate_risk_adjusted_yield(self,
                                       apy: float,
                                       risk_score: float,
                                       tvl: float) -> float:
        """
        Calculate risk-adjusted yield.
        
        Risk-Adjusted APY = APY × (1 - Risk_Score) × TVL_Factor
        
        Args:
            apy: Protocol APY
            risk_score: Protocol risk score (0-1)
            tvl: Total value locked
            
        Returns:
            Risk-adjusted APY
        """
        # TVL factor (larger TVL = safer)
        tvl_factor = min(tvl / 100000000, 1.2)  # Cap at 1.2x for $100M+ TVL
        
        # Risk adjustment
        risk_adjustment = 1 - (risk_score * 0.7)  # Max 70% reduction for high risk
        
        risk_adjusted = apy * risk_adjustment * tvl_factor
        
        return risk_adjusted
    
    def _calculate_opportunity_score(self,
                                     risk_adjusted_apy: float,
                                     tvl: float,
                                     risk_score: float) -> float:
        """
        Calculate yield opportunity score.
        
        Args:
            risk_adjusted_apy: Risk-adjusted APY
            tvl: Total value locked
            risk_score: Risk score
            
        Returns:
            Opportunity score (higher is better)
        """
        # APY component (weight: 60%)
        apy_score = risk_adjusted_apy * 60
        
        # Safety component (weight: 25%)
        safety_score = (1 - risk_score) * 25
        
        # Liquidity component (weight: 15%)
        liquidity_score = min(tvl / 10000000, 1.0) * 15
        
        return apy_score + safety_score + liquidity_score
    
    def generate_signal(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate yield optimization signal."""
        best_opp = analysis.get('best_opportunity')
        opportunities = analysis.get('opportunities', [])
        
        if not best_opp:
            return {
                'action': 'HOLD',
                'confidence': 0.0,
                'reason': 'No suitable yield opportunities'
            }
        
        # Check if rebalancing is needed
        current_allocation = best_opp.get('current_allocation', 0)
        
        if current_allocation > 0:
            # Already allocated, check if better opportunity exists
            current_protocol = best_opp
            
            # Find if there's a significantly better protocol
            better_protocols = [
                opp for opp in opportunities
                if opp['opportunity_score'] > current_protocol['opportunity_score'] * (1 + self.rebalance_threshold)
            ]
            
            if not better_protocols:
                return {
                    'action': 'HOLD',
                    'confidence': 0.5,
                    'reason': 'Current allocation is optimal'
                }
        
        # Calculate confidence based on opportunity score
        confidence = min(best_opp['opportunity_score'] / 50, 1.0)
        
        return {
            'action': 'OPTIMIZE_YIELD',
            'confidence': confidence,
            'target_protocol': best_opp['protocol'],
            'expected_apy': best_opp['apy'],
            'risk_adjusted_apy': best_opp['risk_adjusted_apy'],
            'risk_score': best_opp['risk_score'],
            'tvl': best_opp['tvl'],
            'opportunity_score': best_opp['opportunity_score'],
        }
    
    def calculate_position_size(self,
                               signal: Dict[str, Any],
                               portfolio_value: float,
                               risk_params: Dict[str, Any]) -> float:
        """Calculate position size for yield farming."""
        if signal['action'] == 'HOLD':
            return 0.0
        
        risk_adjusted_apy = signal.get('risk_adjusted_apy', 0)
        risk_score = signal.get('risk_score', 0.5)
        
        max_position = risk_params.get('max_position_size', 0.4)
        
        # Allocate more to safer, higher-yield protocols
        safety_factor = 1 - risk_score
        yield_factor = min(risk_adjusted_apy / 0.5, 1.0)  # Normalize to 50% APY
        
        optimal_size = min(
            max_position,
            0.2 * safety_factor * yield_factor + 0.1  # Base 10% + performance-based
        )
        
        return max(optimal_size, 0.05)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get strategy performance metrics."""
        metrics = super().get_performance_metrics()
        
        metrics.update({
            'protocols_monitored': self.protocols_monitored,
            'rebalances_executed': self.rebalances_executed,
            'total_yield_earned': self.total_yield_earned,
        })
        
        return metrics
