"""
Liquidation Hunter Strategy
============================

Elite strategy for hunting underwater positions and executing profitable liquidations.
Targets 10-100% profit per liquidation with minimal risk.
"""

from typing import Dict, Any, List
from .base_strategy import BaseStrategy
from ..config import Config
import logging

logger = logging.getLogger(__name__)


class LiquidationHunterStrategy(BaseStrategy):
    """
    Liquidation hunting strategy for lending protocol opportunities.
    
    This strategy:
    - Monitors lending protocols for positions near liquidation
    - Calculates optimal liquidation timing
    - Estimates liquidation profitability including gas costs
    - Executes liquidations for maximum profit
    """
    
    def __init__(self,
                 min_health_factor: float = None,
                 min_liquidation_profit: float = None,
                 max_gas_price: float = None):
        """
        Initialize Liquidation Hunter Strategy.
        
        Args:
            min_health_factor: Minimum health factor to monitor (defaults to config)
            min_liquidation_profit: Minimum profit threshold (defaults to config)
            max_gas_price: Maximum gas price in gwei (defaults to config)
        """
        super().__init__(
            name="Liquidation Hunter",
            description="Elite liquidation hunting strategy"
        )
        
        # Load from config if not provided
        self.min_health_factor = (
            min_health_factor if min_health_factor is not None 
            else Config.get_liquidation_min_health_factor()
        )
        self.min_liquidation_profit = (
            min_liquidation_profit if min_liquidation_profit is not None 
            else Config.get_liquidation_min_profit()
        )
        self.max_gas_price = (
            max_gas_price if max_gas_price is not None 
            else Config.get_max_gas_price_gwei()
        )
        
        logger.info(f"Liquidation Hunter initialized with config: "
                   f"min_health_factor={self.min_health_factor:.2f}, "
                   f"min_profit={self.min_liquidation_profit*100:.2f}%, "
                   f"max_gas={self.max_gas_price} gwei")
        
        self.positions_monitored = 0
        self.liquidations_executed = 0
        self.average_liquidation_profit = 0.0
    
    def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze lending protocols for liquidation opportunities.
        
        Args:
            market_data: Market data including protocol positions
            
        Returns:
            Analysis with liquidation opportunities
        """
        positions = market_data.get('lending_positions', [])
        current_prices = market_data.get('asset_prices', {})
        gas_price = market_data.get('gas_price', 50)
        
        if not positions:
            return {'opportunities': [], 'best_opportunity': None}
        
        opportunities = []
        self.positions_monitored += len(positions)
        
        for position in positions:
            # Calculate health factor
            health_factor = self._calculate_health_factor(position, current_prices)
            
            if health_factor >= self.min_health_factor:
                continue  # Position is healthy
            
            # Calculate liquidation profitability
            liquidation_profit = self._calculate_liquidation_profit(
                position, current_prices, gas_price
            )
            
            if liquidation_profit >= self.min_liquidation_profit:
                opportunities.append({
                    'position_id': position.get('id'),
                    'protocol': position.get('protocol', 'Unknown'),
                    'collateral_asset': position.get('collateral_asset'),
                    'debt_asset': position.get('debt_asset'),
                    'collateral_amount': position.get('collateral_amount', 0),
                    'debt_amount': position.get('debt_amount', 0),
                    'health_factor': health_factor,
                    'liquidation_profit': liquidation_profit,
                    'liquidation_bonus': position.get('liquidation_bonus', 0.05),
                    'urgency_score': self._calculate_urgency_score(health_factor),
                })
        
        # Sort by profit potential and urgency
        opportunities.sort(
            key=lambda x: x['liquidation_profit'] * x['urgency_score'],
            reverse=True
        )
        
        return {
            'opportunities': opportunities,
            'best_opportunity': opportunities[0] if opportunities else None,
            'total_opportunities': len(opportunities),
        }
    
    def _calculate_health_factor(self, 
                                 position: Dict[str, Any],
                                 prices: Dict[str, float]) -> float:
        """
        Calculate position health factor.
        
        Health Factor = (Collateral Value × Liquidation Threshold) / Debt Value
        
        Args:
            position: Position data
            prices: Current asset prices
            
        Returns:
            Health factor (< 1.0 = liquidatable)
        """
        collateral_asset = position.get('collateral_asset', '')
        debt_asset = position.get('debt_asset', '')
        collateral_amount = position.get('collateral_amount', 0)
        debt_amount = position.get('debt_amount', 0)
        liquidation_threshold = position.get('liquidation_threshold', 0.8)
        
        collateral_price = prices.get(collateral_asset, 0)
        debt_price = prices.get(debt_asset, 0)
        
        if debt_price == 0 or debt_amount == 0:
            return float('inf')
        
        collateral_value = collateral_amount * collateral_price
        debt_value = debt_amount * debt_price
        
        health_factor = (collateral_value * liquidation_threshold) / debt_value
        
        return health_factor
    
    def _calculate_liquidation_profit(self,
                                      position: Dict[str, Any],
                                      prices: Dict[str, float],
                                      gas_price: float) -> float:
        """
        Calculate expected profit from liquidation.
        
        Args:
            position: Position data
            prices: Current asset prices
            gas_price: Current gas price
            
        Returns:
            Expected profit percentage
        """
        liquidation_bonus = position.get('liquidation_bonus', 0.05)
        collateral_asset = position.get('collateral_asset', '')
        debt_asset = position.get('debt_asset', '')
        debt_amount = position.get('debt_amount', 0)
        
        collateral_price = prices.get(collateral_asset, 0)
        debt_price = prices.get(debt_asset, 0)
        
        # Amount of debt we can liquidate (typically 50% of position)
        max_liquidation_pct = position.get('max_liquidation_pct', 0.5)
        liquidatable_debt = debt_amount * max_liquidation_pct
        
        # Value we need to pay
        liquidation_value = liquidatable_debt * debt_price
        
        # Collateral we receive (with bonus)
        collateral_received = (liquidatable_debt * debt_price / collateral_price) * (1 + liquidation_bonus)
        collateral_value = collateral_received * collateral_price
        
        # Gross profit
        gross_profit = collateral_value - liquidation_value
        
        # Estimate gas cost (liquidations use ~300k gas)
        gas_cost = self._estimate_gas_cost(gas_price, 300000)
        
        # Net profit
        net_profit = gross_profit - gas_cost
        
        # Return as percentage of capital required
        if liquidation_value > 0:
            return net_profit / liquidation_value
        return 0.0
    
    def _estimate_gas_cost(self, gas_price: float, gas_units: int) -> float:
        """Estimate gas cost in USD."""
        eth_price = 2000  # Simplified
        cost_eth = (gas_units * gas_price) / 1e9
        return cost_eth * eth_price
    
    def _calculate_urgency_score(self, health_factor: float) -> float:
        """
        Calculate urgency score based on health factor.
        
        Lower health factor = higher urgency
        
        Args:
            health_factor: Position health factor
            
        Returns:
            Urgency score (0-10)
        """
        if health_factor < 1.0:
            return 10.0  # Critical - liquidatable now
        elif health_factor < 1.01:
            return 8.0   # Very high urgency
        elif health_factor < 1.02:
            return 5.0   # High urgency
        elif health_factor < 1.03:
            return 3.0   # Medium urgency
        else:
            return 1.0   # Low urgency
    
    def generate_signal(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate liquidation signal."""
        best_opp = analysis.get('best_opportunity')
        
        if not best_opp:
            return {
                'action': 'HOLD',
                'confidence': 0.0,
                'reason': 'No liquidation opportunities found'
            }
        
        # Confidence based on profit and urgency
        confidence = min(
            (best_opp['liquidation_profit'] * 10 + best_opp['urgency_score'] / 10),
            1.0
        )
        
        return {
            'action': 'EXECUTE_LIQUIDATION',
            'confidence': confidence,
            'position_id': best_opp['position_id'],
            'protocol': best_opp['protocol'],
            'expected_profit': best_opp['liquidation_profit'],
            'health_factor': best_opp['health_factor'],
            'urgency': best_opp['urgency_score'],
            'collateral_asset': best_opp['collateral_asset'],
            'debt_asset': best_opp['debt_asset'],
        }
    
    def calculate_position_size(self,
                               signal: Dict[str, Any],
                               portfolio_value: float,
                               risk_params: Dict[str, Any]) -> float:
        """Calculate position size for liquidation."""
        if signal['action'] == 'HOLD':
            return 0.0
        
        expected_profit = signal['expected_profit']
        urgency = signal['urgency']
        
        max_position = risk_params.get('max_position_size', 0.25)
        
        # Higher urgency and profit = larger position
        optimal_size = min(
            max_position,
            expected_profit * 2 * (urgency / 10)
        )
        
        return max(optimal_size, 0.03)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get strategy performance metrics."""
        metrics = super().get_performance_metrics()
        
        metrics.update({
            'positions_monitored': self.positions_monitored,
            'liquidations_executed': self.liquidations_executed,
            'average_liquidation_profit': self.average_liquidation_profit,
        })
        
        return metrics
