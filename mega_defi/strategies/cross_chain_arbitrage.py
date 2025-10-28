"""
Cross-Chain Arbitrage Strategy
===============================

Advanced strategy for exploiting price differences across blockchain networks.
Targets 3-15% profit per trade with cross-chain bridge opportunities.
"""

from typing import Dict, Any, List
from .base_strategy import BaseStrategy
import logging

logger = logging.getLogger(__name__)


class CrossChainArbitrageStrategy(BaseStrategy):
    """
    Cross-chain arbitrage strategy for multi-chain opportunities.
    
    This strategy:
    - Monitors prices across multiple blockchain networks
    - Identifies profitable cross-chain arbitrage opportunities
    - Accounts for bridge fees and time delays
    - Optimizes for maximum profit after all costs
    """
    
    def __init__(self,
                 min_profit_after_fees: float = 0.03,
                 max_bridge_time: int = 600,
                 supported_chains: List[str] = None):
        """
        Initialize Cross-Chain Arbitrage Strategy.
        
        Args:
            min_profit_after_fees: Minimum profit after all fees (default 3%)
            max_bridge_time: Maximum acceptable bridge time in seconds
            supported_chains: List of supported blockchain networks
        """
        super().__init__(
            name="Cross-Chain Arbitrage",
            description="Advanced multi-chain arbitrage strategy"
        )
        
        self.min_profit_after_fees = min_profit_after_fees
        self.max_bridge_time = max_bridge_time
        self.supported_chains = supported_chains or [
            'Ethereum', 'BSC', 'Polygon', 'Arbitrum', 'Optimism', 'Avalanche'
        ]
        
        # Bridge fee estimates (percentage)
        self.bridge_fees = {
            ('Ethereum', 'BSC'): 0.001,
            ('Ethereum', 'Polygon'): 0.001,
            ('Ethereum', 'Arbitrum'): 0.0005,
            ('Ethereum', 'Optimism'): 0.0005,
            ('BSC', 'Polygon'): 0.002,
            ('BSC', 'Avalanche'): 0.002,
        }
        
        self.cross_chain_opportunities = 0
        self.successful_bridges = 0
    
    def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze cross-chain arbitrage opportunities.
        
        Args:
            market_data: Market data with multi-chain prices
            
        Returns:
            Analysis with cross-chain opportunities
        """
        chains_data = market_data.get('chains', {})
        
        if len(chains_data) < 2:
            return {'opportunities': [], 'best_opportunity': None}
        
        opportunities = []
        
        # Compare prices across all chain pairs
        chain_names = list(chains_data.keys())
        
        for i in range(len(chain_names)):
            for j in range(i + 1, len(chain_names)):
                chain_a = chain_names[i]
                chain_b = chain_names[j]
                
                if chain_a not in self.supported_chains or chain_b not in self.supported_chains:
                    continue
                
                data_a = chains_data[chain_a]
                data_b = chains_data[chain_b]
                
                price_a = data_a.get('price', 0)
                price_b = data_b.get('price', 0)
                liquidity_a = data_a.get('liquidity', 0)
                liquidity_b = data_b.get('liquidity', 0)
                
                if price_a <= 0 or price_b <= 0:
                    continue
                
                # Determine trade direction
                if price_a < price_b:
                    buy_chain = chain_a
                    sell_chain = chain_b
                    buy_price = price_a
                    sell_price = price_b
                else:
                    buy_chain = chain_b
                    sell_chain = chain_a
                    buy_price = price_b
                    sell_price = price_a
                
                # Calculate gross profit
                gross_profit_pct = (sell_price - buy_price) / buy_price
                
                # Get bridge fee
                bridge_fee = self._get_bridge_fee(buy_chain, sell_chain)
                
                # Calculate net profit after fees
                net_profit_pct = gross_profit_pct - bridge_fee - 0.006  # 0.3% DEX fees each side
                
                # Estimate bridge time
                bridge_time = self._estimate_bridge_time(buy_chain, sell_chain)
                
                # Check if opportunity is profitable
                if (net_profit_pct >= self.min_profit_after_fees and
                    bridge_time <= self.max_bridge_time):
                    
                    opportunity_score = self._calculate_opportunity_score(
                        net_profit_pct,
                        min(liquidity_a, liquidity_b),
                        bridge_time,
                        bridge_fee
                    )
                    
                    opportunities.append({
                        'buy_chain': buy_chain,
                        'sell_chain': sell_chain,
                        'buy_price': buy_price,
                        'sell_price': sell_price,
                        'gross_profit': gross_profit_pct,
                        'net_profit': net_profit_pct,
                        'bridge_fee': bridge_fee,
                        'bridge_time': bridge_time,
                        'liquidity': min(liquidity_a, liquidity_b),
                        'opportunity_score': opportunity_score,
                    })
        
        # Sort by opportunity score
        opportunities.sort(key=lambda x: x['opportunity_score'], reverse=True)
        
        self.cross_chain_opportunities += len(opportunities)
        
        return {
            'opportunities': opportunities,
            'best_opportunity': opportunities[0] if opportunities else None,
            'total_opportunities': len(opportunities),
        }
    
    def _get_bridge_fee(self, chain_a: str, chain_b: str) -> float:
        """Get bridge fee between two chains."""
        key = (chain_a, chain_b)
        reverse_key = (chain_b, chain_a)
        
        if key in self.bridge_fees:
            return self.bridge_fees[key]
        elif reverse_key in self.bridge_fees:
            return self.bridge_fees[reverse_key]
        else:
            return 0.002  # Default 0.2% bridge fee
    
    def _estimate_bridge_time(self, chain_a: str, chain_b: str) -> int:
        """
        Estimate bridge time in seconds.
        
        Args:
            chain_a: Source chain
            chain_b: Destination chain
            
        Returns:
            Estimated time in seconds
        """
        # Layer 2s are faster
        l2_chains = {'Arbitrum', 'Optimism', 'Polygon'}
        
        if chain_a in l2_chains and chain_b in l2_chains:
            return 180  # 3 minutes for L2 to L2
        elif chain_a in l2_chains or chain_b in l2_chains:
            return 420  # 7 minutes for L2 to L1 or vice versa
        else:
            return 600  # 10 minutes for L1 to L1
    
    def _calculate_opportunity_score(self,
                                    net_profit: float,
                                    liquidity: float,
                                    bridge_time: int,
                                    bridge_fee: float) -> float:
        """
        Calculate opportunity score for cross-chain arbitrage.
        
        Args:
            net_profit: Net profit percentage
            liquidity: Available liquidity
            bridge_time: Bridge time in seconds
            bridge_fee: Bridge fee percentage
            
        Returns:
            Opportunity score (higher is better)
        """
        # Profit component (weight: 50%)
        profit_score = net_profit * 100
        
        # Liquidity component (weight: 25%)
        liquidity_score = min(liquidity / 50000, 10.0)
        
        # Speed component (weight: 15%)
        speed_score = max(10 - (bridge_time / 60), 0)
        
        # Fee efficiency component (weight: 10%)
        fee_score = max(10 - (bridge_fee * 500), 0)
        
        # Weighted score
        score = (
            profit_score * 0.50 +
            liquidity_score * 0.25 +
            speed_score * 0.15 +
            fee_score * 0.10
        )
        
        return score
    
    def generate_signal(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate trading signal from analysis.
        
        Args:
            analysis: Analysis results
            
        Returns:
            Trading signal with parameters
        """
        best_opp = analysis.get('best_opportunity')
        
        if not best_opp:
            return {
                'action': 'HOLD',
                'confidence': 0.0,
                'reason': 'No cross-chain opportunities found'
            }
        
        # Calculate confidence based on opportunity score
        confidence = min(best_opp['opportunity_score'] / 30, 1.0)
        
        return {
            'action': 'EXECUTE_CROSS_CHAIN',
            'confidence': confidence,
            'buy_chain': best_opp['buy_chain'],
            'sell_chain': best_opp['sell_chain'],
            'buy_price': best_opp['buy_price'],
            'sell_price': best_opp['sell_price'],
            'expected_profit': best_opp['net_profit'],
            'gross_profit': best_opp['gross_profit'],
            'bridge_fee': best_opp['bridge_fee'],
            'bridge_time': best_opp['bridge_time'],
            'liquidity': best_opp['liquidity'],
            'opportunity_score': best_opp['opportunity_score'],
        }
    
    def calculate_position_size(self,
                               signal: Dict[str, Any],
                               portfolio_value: float,
                               risk_params: Dict[str, Any]) -> float:
        """
        Calculate position size for cross-chain arbitrage.
        
        Args:
            signal: Trading signal
            portfolio_value: Current portfolio value
            risk_params: Risk parameters
            
        Returns:
            Position size as fraction of portfolio
        """
        if signal['action'] == 'HOLD':
            return 0.0
        
        # Get parameters
        expected_profit = signal['expected_profit']
        bridge_time = signal['bridge_time']
        liquidity = signal.get('liquidity', 0)
        
        # Max position from risk params
        max_position = risk_params.get('max_position_size', 0.15)
        
        # Time risk adjustment (longer bridge time = smaller position)
        time_factor = max(1.0 - (bridge_time / self.max_bridge_time) * 0.5, 0.5)
        
        # Calculate optimal size
        optimal_size = min(
            liquidity / portfolio_value * 0.5,  # Use 50% of available liquidity
            max_position,
            expected_profit * 3 * time_factor   # Profit-based sizing with time adjustment
        )
        
        return max(optimal_size, 0.02)  # Minimum 2% position
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get strategy performance metrics."""
        metrics = super().get_performance_metrics()
        
        # Add strategy-specific metrics
        metrics.update({
            'cross_chain_opportunities': self.cross_chain_opportunities,
            'successful_bridges': self.successful_bridges,
            'bridge_success_rate': (self.successful_bridges / self.cross_chain_opportunities
                                   if self.cross_chain_opportunities > 0 else 0),
            'supported_chains': len(self.supported_chains),
        })
        
        return metrics
