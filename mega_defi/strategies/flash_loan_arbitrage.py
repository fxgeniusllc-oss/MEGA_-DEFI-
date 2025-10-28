"""
Flash Loan Arbitrage Strategy
==============================

Elite strategy for exploiting price differences across DEXs using flash loans.
Targets 5-50% profit per trade with zero capital requirements.
"""

from typing import Dict, Any, List
from .base_strategy import BaseStrategy
from ..config import Config
import logging

logger = logging.getLogger(__name__)


class FlashLoanArbitrageStrategy(BaseStrategy):
    """
    Flash loan arbitrage strategy with TAR (Total Arbitrage Return) scoring.
    
    This strategy:
    - Identifies price differences across multiple DEXs
    - Calculates optimal trade paths
    - Uses flash loans to maximize capital efficiency
    - Scores opportunities using TAR methodology
    """
    
    def __init__(self, 
                 min_profit_threshold: float = None,
                 max_gas_cost: float = None,
                 min_liquidity: float = None):
        """
        Initialize Flash Loan Arbitrage Strategy.
        
        Args:
            min_profit_threshold: Minimum profit threshold (defaults to config)
            max_gas_cost: Maximum acceptable gas cost in USD (defaults to config)
            min_liquidity: Minimum liquidity requirement in USD (defaults to config)
        """
        super().__init__(
            name="Flash Loan Arbitrage",
            description="Elite flash loan arbitrage with TAR scoring"
        )
        
        # Load from config if not provided
        self.min_profit_threshold = (
            min_profit_threshold if min_profit_threshold is not None 
            else Config.get_flash_loan_min_profit()
        )
        self.max_gas_cost = (
            max_gas_cost if max_gas_cost is not None 
            else Config.get_arbitrage_max_gas_cost()
        )
        self.min_liquidity = (
            min_liquidity if min_liquidity is not None 
            else Config.get_arbitrage_min_liquidity()
        )
        
        logger.info(f"Flash Loan Arbitrage initialized with config: "
                   f"min_profit={self.min_profit_threshold*100:.2f}%, "
                   f"max_gas=${self.max_gas_cost}, "
                   f"min_liquidity=${self.min_liquidity:,.0f}")
        
        # Strategy-specific tracking
        self.opportunities_found = 0
        self.opportunities_executed = 0
        self.total_tar_score = 0.0
    
    def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze market for flash loan arbitrage opportunities.
        
        Args:
            market_data: Market data including exchange prices
            
        Returns:
            Analysis with opportunities and TAR scores
        """
        exchanges = market_data.get('exchanges', [])
        
        if len(exchanges) < 2:
            return {'opportunities': [], 'best_opportunity': None}
        
        opportunities = []
        
        # Find arbitrage opportunities between all exchange pairs
        for i in range(len(exchanges)):
            for j in range(i + 1, len(exchanges)):
                exchange_a = exchanges[i]
                exchange_b = exchanges[j]
                
                price_a = exchange_a.get('price', 0)
                price_b = exchange_b.get('price', 0)
                liquidity_a = exchange_a.get('liquidity', 0)
                liquidity_b = exchange_b.get('liquidity', 0)
                
                if price_a <= 0 or price_b <= 0:
                    continue
                
                # Calculate price difference
                if price_a < price_b:
                    buy_exchange = exchange_a['name']
                    sell_exchange = exchange_b['name']
                    buy_price = price_a
                    sell_price = price_b
                    available_liquidity = min(liquidity_a, liquidity_b)
                else:
                    buy_exchange = exchange_b['name']
                    sell_exchange = exchange_a['name']
                    buy_price = price_b
                    sell_price = price_a
                    available_liquidity = min(liquidity_a, liquidity_b)
                
                # Calculate profit percentage
                profit_pct = (sell_price - buy_price) / buy_price
                
                # Calculate TAR score
                tar_score = self._calculate_tar_score(
                    profit_pct,
                    available_liquidity,
                    market_data.get('gas_price', 50)
                )
                
                # Check if opportunity meets criteria
                if (profit_pct >= self.min_profit_threshold and
                    available_liquidity >= self.min_liquidity and
                    tar_score > 0):
                    
                    opportunities.append({
                        'buy_exchange': buy_exchange,
                        'sell_exchange': sell_exchange,
                        'buy_price': buy_price,
                        'sell_price': sell_price,
                        'profit_percentage': profit_pct,
                        'available_liquidity': available_liquidity,
                        'tar_score': tar_score,
                        'estimated_gas_cost': self._estimate_gas_cost(market_data.get('gas_price', 50)),
                    })
        
        # Sort by TAR score
        opportunities.sort(key=lambda x: x['tar_score'], reverse=True)
        
        self.opportunities_found += len(opportunities)
        
        return {
            'opportunities': opportunities,
            'best_opportunity': opportunities[0] if opportunities else None,
            'total_opportunities': len(opportunities),
        }
    
    def _calculate_tar_score(self, 
                            profit_pct: float,
                            liquidity: float,
                            gas_price: float) -> float:
        """
        Calculate Total Arbitrage Return (TAR) score.
        
        TAR Formula:
        TAR = (Profit% × Liquidity × Execution_Probability) - Gas_Cost_Impact
        
        Args:
            profit_pct: Profit percentage
            liquidity: Available liquidity
            gas_price: Current gas price
            
        Returns:
            TAR score (higher is better)
        """
        # Execution probability based on profit margin
        execution_prob = min(profit_pct / 0.02, 1.0)  # 2% = 100% probability
        
        # Liquidity score (normalized)
        liquidity_score = min(liquidity / 100000, 10.0)
        
        # Gas cost impact (negative factor)
        gas_cost = self._estimate_gas_cost(gas_price)
        gas_impact = min(gas_cost / self.max_gas_cost, 1.0)
        
        # Calculate TAR
        tar_score = (
            profit_pct * 100 *           # Convert to percentage points
            liquidity_score *             # Liquidity factor
            execution_prob                # Execution probability
        ) - (gas_impact * 10)            # Gas cost penalty
        
        return max(tar_score, 0)
    
    def _estimate_gas_cost(self, gas_price: float) -> float:
        """
        Estimate gas cost for flash loan arbitrage.
        
        Args:
            gas_price: Gas price in gwei
            
        Returns:
            Estimated gas cost in USD
        """
        # Flash loan arbitrage typically uses 300k-500k gas
        gas_units = 400000
        eth_price = 2000  # Simplified, should be from market data
        
        cost_eth = (gas_units * gas_price) / 1e9
        cost_usd = cost_eth * eth_price
        
        return cost_usd
    
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
                'reason': 'No arbitrage opportunities found'
            }
        
        # Calculate confidence based on TAR score
        confidence = min(best_opp['tar_score'] / 50, 1.0)
        
        return {
            'action': 'EXECUTE_ARBITRAGE',
            'confidence': confidence,
            'buy_exchange': best_opp['buy_exchange'],
            'sell_exchange': best_opp['sell_exchange'],
            'buy_price': best_opp['buy_price'],
            'sell_price': best_opp['sell_price'],
            'expected_profit': best_opp['profit_percentage'],
            'tar_score': best_opp['tar_score'],
            'liquidity': best_opp['available_liquidity'],
            'estimated_gas': best_opp['estimated_gas_cost'],
        }
    
    def calculate_position_size(self,
                               signal: Dict[str, Any],
                               portfolio_value: float,
                               risk_params: Dict[str, Any]) -> float:
        """
        Calculate position size for flash loan arbitrage.
        
        For flash loans, position size is limited by:
        1. Available liquidity on DEXs
        2. Flash loan provider limits
        3. Risk management parameters
        
        Args:
            signal: Trading signal
            portfolio_value: Current portfolio value
            risk_params: Risk parameters
            
        Returns:
            Position size as fraction of portfolio
        """
        if signal['action'] == 'HOLD':
            return 0.0
        
        # Get available liquidity
        available_liquidity = signal.get('liquidity', 0)
        
        # Max position from risk params
        max_position = risk_params.get('max_position_size', 0.2)
        
        # Calculate optimal size based on liquidity and profit
        profit_pct = signal['expected_profit']
        optimal_size = min(
            available_liquidity / portfolio_value,  # Liquidity constraint
            max_position,                            # Risk constraint
            profit_pct * 5                           # Profit-based scaling
        )
        
        return max(optimal_size, 0.01)  # Minimum 1% position
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get strategy performance metrics."""
        metrics = super().get_performance_metrics()
        
        # Add strategy-specific metrics
        metrics.update({
            'opportunities_found': self.opportunities_found,
            'opportunities_executed': self.opportunities_executed,
            'execution_rate': (self.opportunities_executed / self.opportunities_found 
                             if self.opportunities_found > 0 else 0),
            'average_tar_score': (self.total_tar_score / self.opportunities_executed
                                 if self.opportunities_executed > 0 else 0),
        })
        
        return metrics
