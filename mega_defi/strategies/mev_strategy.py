"""
MEV (Maximal Extractable Value) Strategy
========================================

Elite strategy for sandwich attacks, front-running detection, and MEV opportunities.
Targets 5-200% profit per transaction with minimal risk.
"""

from typing import Dict, Any, List
from .base_strategy import BaseStrategy
from ..config import Config
import logging

logger = logging.getLogger(__name__)


class MEVStrategy(BaseStrategy):
    """
    MEV strategy for extracting value from transaction ordering.
    
    This strategy:
    - Detects large pending transactions (mempool monitoring)
    - Identifies sandwich attack opportunities
    - Calculates optimal front-run and back-run transactions
    - Executes MEV bundles for guaranteed profit
    """
    
    def __init__(self,
                 min_transaction_size: float = None,
                 min_expected_profit: float = None,
                 max_slippage_impact: float = None):
        """
        Initialize MEV Strategy.
        
        Args:
            min_transaction_size: Minimum transaction size to target in USD (defaults to config)
            min_expected_profit: Minimum expected profit percentage (defaults to config)
            max_slippage_impact: Maximum slippage impact we can cause (defaults to config)
        """
        super().__init__(
            name="MEV Strategy",
            description="Elite MEV extraction and sandwich attack strategy"
        )
        
        # Load from config if not provided
        self.min_transaction_size = (
            min_transaction_size if min_transaction_size is not None 
            else Config.get_mev_min_transaction_size()
        )
        self.min_expected_profit = (
            min_expected_profit if min_expected_profit is not None 
            else Config.get_mev_min_expected_profit()
        )
        self.max_slippage_impact = (
            max_slippage_impact if max_slippage_impact is not None 
            else Config.get_max_slippage()
        )
        
        logger.info(f"MEV Strategy initialized with config: "
                   f"min_tx_size=${self.min_transaction_size:,.0f}, "
                   f"min_profit={self.min_expected_profit*100:.2f}%, "
                   f"max_slippage={self.max_slippage_impact*100:.2f}%")
        
        self.mev_opportunities_detected = 0
        self.sandwich_attacks_executed = 0
        self.front_run_successes = 0
    
    def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze mempool for MEV opportunities.
        
        Args:
            market_data: Market data including pending transactions
            
        Returns:
            Analysis with MEV opportunities
        """
        pending_txs = market_data.get('pending_transactions', [])
        pool_data = market_data.get('liquidity_pools', {})
        
        if not pending_txs:
            return {'opportunities': [], 'best_opportunity': None}
        
        opportunities = []
        
        for tx in pending_txs:
            # Analyze transaction for MEV potential
            if not self._is_mev_target(tx):
                continue
            
            # Calculate sandwich attack profitability
            sandwich_result = self._calculate_sandwich_profit(tx, pool_data)
            
            if sandwich_result and sandwich_result['profit'] >= self.min_expected_profit:
                opportunities.append({
                    'type': 'sandwich',
                    'target_tx': tx.get('hash'),
                    'target_size': tx.get('value', 0),
                    'pool': tx.get('pool'),
                    'token_in': tx.get('token_in'),
                    'token_out': tx.get('token_out'),
                    'front_run_amount': sandwich_result['front_run_amount'],
                    'back_run_amount': sandwich_result['back_run_amount'],
                    'expected_profit': sandwich_result['profit'],
                    'slippage_caused': sandwich_result['slippage'],
                    'mev_score': sandwich_result['mev_score'],
                })
        
        # Sort by MEV score
        opportunities.sort(key=lambda x: x['mev_score'], reverse=True)
        
        self.mev_opportunities_detected += len(opportunities)
        
        return {
            'opportunities': opportunities,
            'best_opportunity': opportunities[0] if opportunities else None,
            'total_opportunities': len(opportunities),
        }
    
    def _is_mev_target(self, tx: Dict[str, Any]) -> bool:
        """
        Determine if transaction is a valid MEV target.
        
        Args:
            tx: Transaction data
            
        Returns:
            True if transaction is MEV target
        """
        tx_value = tx.get('value', 0)
        tx_type = tx.get('type', '')
        gas_price = tx.get('gas_price', 0)
        
        # Must be a swap transaction with significant size
        if tx_type not in ['swap', 'trade']:
            return False
        
        if tx_value < self.min_transaction_size:
            return False
        
        # Must have reasonable gas price (not trying to front-run us)
        if gas_price > 500:  # 500 gwei
            return False
        
        return True
    
    def _calculate_sandwich_profit(self,
                                   target_tx: Dict[str, Any],
                                   pool_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate profitability of sandwich attack.
        
        Sandwich attack:
        1. Front-run: Buy before victim
        2. Victim trades: Pushes price up
        3. Back-run: Sell after victim
        
        Args:
            target_tx: Target transaction
            pool_data: Liquidity pool data
            
        Returns:
            Sandwich attack parameters and profitability
        """
        pool_id = target_tx.get('pool')
        target_amount = target_tx.get('value', 0)
        
        pool = pool_data.get(pool_id, {})
        reserve_in = pool.get('reserve_in', 0)
        reserve_out = pool.get('reserve_out', 0)
        
        if reserve_in == 0 or reserve_out == 0:
            return None
        
        # Calculate optimal front-run size (fraction of target)
        optimal_front_run = self._calculate_optimal_front_run(
            target_amount, reserve_in, reserve_out
        )
        
        if optimal_front_run == 0:
            return None
        
        # Simulate price impact
        # Front-run effect
        new_reserve_in = reserve_in + optimal_front_run
        tokens_out_front = self._get_amount_out(optimal_front_run, reserve_in, reserve_out)
        new_reserve_out = reserve_out - tokens_out_front
        
        # Victim trade effect
        new_reserve_in2 = new_reserve_in + target_amount
        tokens_out_victim = self._get_amount_out(target_amount, new_reserve_in, new_reserve_out)
        new_reserve_out2 = new_reserve_out - tokens_out_victim
        
        # Back-run: sell what we bought
        tokens_in_back = tokens_out_front
        tokens_out_back = self._get_amount_out(tokens_in_back, new_reserve_out2, new_reserve_in2)
        
        # Calculate profit
        profit_amount = tokens_out_back - optimal_front_run
        profit_pct = profit_amount / optimal_front_run if optimal_front_run > 0 else 0
        
        # Calculate slippage caused to victim
        original_price = reserve_out / reserve_in
        victim_price = tokens_out_victim / target_amount
        slippage = abs(victim_price - original_price) / original_price
        
        # Check constraints
        if slippage > self.max_slippage_impact:
            return None  # Would cause too much slippage (detectable/unfair)
        
        # Calculate MEV score
        mev_score = self._calculate_mev_score(
            profit_pct, target_amount, slippage
        )
        
        return {
            'front_run_amount': optimal_front_run,
            'back_run_amount': tokens_out_front,
            'profit': profit_pct,
            'slippage': slippage,
            'mev_score': mev_score,
        }
    
    def _calculate_optimal_front_run(self,
                                     target_amount: float,
                                     reserve_in: float,
                                     reserve_out: float) -> float:
        """
        Calculate optimal front-run size.
        
        Typically 30-80% of target transaction size.
        
        Args:
            target_amount: Target transaction amount
            reserve_in: Pool reserve (input token)
            reserve_out: Pool reserve (output token)
            
        Returns:
            Optimal front-run amount
        """
        # Use 50% of target as starting point
        optimal = target_amount * 0.5
        
        # Adjust based on pool depth
        pool_depth_ratio = target_amount / reserve_in
        
        if pool_depth_ratio > 0.1:  # Large trade relative to pool
            optimal = target_amount * 0.3  # Use smaller front-run
        elif pool_depth_ratio < 0.01:  # Small trade relative to pool
            optimal = target_amount * 0.7  # Can use larger front-run
        
        return optimal
    
    def _get_amount_out(self, amount_in: float, reserve_in: float, reserve_out: float) -> float:
        """
        Calculate output amount for constant product AMM.
        
        Args:
            amount_in: Input amount
            reserve_in: Input reserve
            reserve_out: Output reserve
            
        Returns:
            Output amount
        """
        if reserve_in == 0 or reserve_out == 0:
            return 0
        
        amount_in_with_fee = amount_in * 0.997  # 0.3% fee
        numerator = amount_in_with_fee * reserve_out
        denominator = reserve_in + amount_in_with_fee
        
        return numerator / denominator if denominator > 0 else 0
    
    def _calculate_mev_score(self,
                            profit_pct: float,
                            target_size: float,
                            slippage: float) -> float:
        """
        Calculate MEV opportunity score.
        
        Args:
            profit_pct: Expected profit percentage
            target_size: Target transaction size
            slippage: Slippage caused
            
        Returns:
            MEV score (higher is better)
        """
        # Profit component (weight: 50%)
        profit_score = profit_pct * 100
        
        # Size component (weight: 30%)
        size_score = min(target_size / 50000, 10)
        
        # Low slippage bonus (weight: 20%)
        slippage_score = max(10 - slippage * 100, 0)
        
        score = (
            profit_score * 0.50 +
            size_score * 0.30 +
            slippage_score * 0.20
        )
        
        return score
    
    def generate_signal(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate MEV execution signal."""
        best_opp = analysis.get('best_opportunity')
        
        if not best_opp:
            return {
                'action': 'HOLD',
                'confidence': 0.0,
                'reason': 'No MEV opportunities found'
            }
        
        # High confidence for good MEV opportunities
        confidence = min(best_opp['mev_score'] / 20, 1.0)
        
        return {
            'action': 'EXECUTE_MEV',
            'confidence': confidence,
            'mev_type': best_opp['type'],
            'target_tx': best_opp['target_tx'],
            'front_run_amount': best_opp['front_run_amount'],
            'back_run_amount': best_opp['back_run_amount'],
            'expected_profit': best_opp['expected_profit'],
            'mev_score': best_opp['mev_score'],
        }
    
    def calculate_position_size(self,
                               signal: Dict[str, Any],
                               portfolio_value: float,
                               risk_params: Dict[str, Any]) -> float:
        """Calculate position size for MEV opportunity."""
        if signal['action'] == 'HOLD':
            return 0.0
        
        front_run_amount = signal.get('front_run_amount', 0)
        expected_profit = signal.get('expected_profit', 0)
        
        max_position = risk_params.get('max_position_size', 0.3)
        
        # MEV is low risk when done correctly
        optimal_size = min(
            front_run_amount / portfolio_value,
            max_position,
            expected_profit * 5  # Scale with profit
        )
        
        return max(optimal_size, 0.02)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get strategy performance metrics."""
        metrics = super().get_performance_metrics()
        
        metrics.update({
            'mev_opportunities_detected': self.mev_opportunities_detected,
            'sandwich_attacks_executed': self.sandwich_attacks_executed,
            'front_run_successes': self.front_run_successes,
        })
        
        return metrics
