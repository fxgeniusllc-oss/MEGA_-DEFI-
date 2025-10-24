"""Comprehensive tests for all 5 trading strategies."""

import unittest
from mega_defi.core.strategy_engine import StrategyEngine, StrategyType, Signal


class TestComprehensiveStrategies(unittest.TestCase):
    """Comprehensive test cases for all trading strategies."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = StrategyEngine()
    
    def test_all_five_strategies_exist(self):
        """Test all 5 strategies can be registered."""
        strategies = [
            StrategyType.ARBITRAGE,
            StrategyType.TREND_FOLLOWING,
            StrategyType.MEAN_REVERSION,
            StrategyType.MOMENTUM,
            StrategyType.LIQUIDITY_PROVISION
        ]
        
        for strategy in strategies:
            self.engine.register_strategy(strategy, {})
        
        self.assertEqual(len(self.engine.active_strategies), 5)
    
    def test_arbitrage_comprehensive(self):
        """Comprehensive tests for arbitrage strategy."""
        self.engine.register_strategy(
            StrategyType.ARBITRAGE,
            {'threshold': 0.01}
        )
        
        # Test case 1: Strong buy signal
        signal = self.engine.execute_strategy(
            StrategyType.ARBITRAGE,
            {'price_difference': 0.025}
        )
        self.assertEqual(signal, Signal.BUY)
        
        # Test case 2: Strong sell signal
        signal = self.engine.execute_strategy(
            StrategyType.ARBITRAGE,
            {'price_difference': -0.025}
        )
        self.assertEqual(signal, Signal.SELL)
        
        # Test case 3: Exactly at threshold (should hold with > comparison)
        signal = self.engine.execute_strategy(
            StrategyType.ARBITRAGE,
            {'price_difference': 0.01}
        )
        self.assertEqual(signal, Signal.HOLD)
        
        # Test case 4: Just below threshold
        signal = self.engine.execute_strategy(
            StrategyType.ARBITRAGE,
            {'price_difference': 0.009}
        )
        self.assertEqual(signal, Signal.HOLD)
        
        # Test case 5: Zero difference
        signal = self.engine.execute_strategy(
            StrategyType.ARBITRAGE,
            {'price_difference': 0}
        )
        self.assertEqual(signal, Signal.HOLD)
        
        # Test case 6: Large price difference
        signal = self.engine.execute_strategy(
            StrategyType.ARBITRAGE,
            {'price_difference': 0.1}
        )
        self.assertEqual(signal, Signal.BUY)
    
    def test_trend_following_comprehensive(self):
        """Comprehensive tests for trend following strategy."""
        self.engine.register_strategy(
            StrategyType.TREND_FOLLOWING,
            {'min_strength': 0.5}
        )
        
        # Test case 1: Strong uptrend
        signal = self.engine.execute_strategy(
            StrategyType.TREND_FOLLOWING,
            {'trend': 0.05, 'trend_strength': 0.8}
        )
        self.assertEqual(signal, Signal.BUY)
        
        # Test case 2: Strong downtrend
        signal = self.engine.execute_strategy(
            StrategyType.TREND_FOLLOWING,
            {'trend': -0.05, 'trend_strength': 0.8}
        )
        self.assertEqual(signal, Signal.SELL)
        
        # Test case 3: Weak uptrend (insufficient strength)
        signal = self.engine.execute_strategy(
            StrategyType.TREND_FOLLOWING,
            {'trend': 0.05, 'trend_strength': 0.3}
        )
        self.assertEqual(signal, Signal.HOLD)
        
        # Test case 4: Exactly at threshold
        signal = self.engine.execute_strategy(
            StrategyType.TREND_FOLLOWING,
            {'trend': 0.05, 'trend_strength': 0.5}
        )
        self.assertEqual(signal, Signal.HOLD)
        
        # Test case 5: No trend
        signal = self.engine.execute_strategy(
            StrategyType.TREND_FOLLOWING,
            {'trend': 0, 'trend_strength': 0.8}
        )
        self.assertEqual(signal, Signal.HOLD)
        
        # Test case 6: Very strong trend
        signal = self.engine.execute_strategy(
            StrategyType.TREND_FOLLOWING,
            {'trend': 0.15, 'trend_strength': 1.0}
        )
        self.assertEqual(signal, Signal.BUY)
    
    def test_mean_reversion_comprehensive(self):
        """Comprehensive tests for mean reversion strategy."""
        self.engine.register_strategy(
            StrategyType.MEAN_REVERSION,
            {'deviation_threshold': 2.0}
        )
        
        # Test case 1: Overbought (high positive deviation)
        signal = self.engine.execute_strategy(
            StrategyType.MEAN_REVERSION,
            {'price_deviation': 3.0}
        )
        self.assertEqual(signal, Signal.SELL)
        
        # Test case 2: Oversold (high negative deviation)
        signal = self.engine.execute_strategy(
            StrategyType.MEAN_REVERSION,
            {'price_deviation': -3.0}
        )
        self.assertEqual(signal, Signal.BUY)
        
        # Test case 3: At threshold (positive)
        signal = self.engine.execute_strategy(
            StrategyType.MEAN_REVERSION,
            {'price_deviation': 2.0}
        )
        self.assertEqual(signal, Signal.HOLD)
        
        # Test case 4: Near mean
        signal = self.engine.execute_strategy(
            StrategyType.MEAN_REVERSION,
            {'price_deviation': 0.5}
        )
        self.assertEqual(signal, Signal.HOLD)
        
        # Test case 5: Extreme overbought
        signal = self.engine.execute_strategy(
            StrategyType.MEAN_REVERSION,
            {'price_deviation': 5.0}
        )
        self.assertEqual(signal, Signal.SELL)
        
        # Test case 6: Extreme oversold
        signal = self.engine.execute_strategy(
            StrategyType.MEAN_REVERSION,
            {'price_deviation': -5.0}
        )
        self.assertEqual(signal, Signal.BUY)
    
    def test_momentum_comprehensive(self):
        """Comprehensive tests for momentum strategy."""
        self.engine.register_strategy(
            StrategyType.MOMENTUM,
            {'momentum_threshold': 0.05}
        )
        
        # Test case 1: Strong positive momentum
        signal = self.engine.execute_strategy(
            StrategyType.MOMENTUM,
            {'momentum': 0.08}
        )
        self.assertEqual(signal, Signal.BUY)
        
        # Test case 2: Strong negative momentum
        signal = self.engine.execute_strategy(
            StrategyType.MOMENTUM,
            {'momentum': -0.08}
        )
        self.assertEqual(signal, Signal.SELL)
        
        # Test case 3: Weak positive momentum
        signal = self.engine.execute_strategy(
            StrategyType.MOMENTUM,
            {'momentum': 0.03}
        )
        self.assertEqual(signal, Signal.HOLD)
        
        # Test case 4: Zero momentum
        signal = self.engine.execute_strategy(
            StrategyType.MOMENTUM,
            {'momentum': 0}
        )
        self.assertEqual(signal, Signal.HOLD)
        
        # Test case 5: At threshold (should hold with > comparison)
        signal = self.engine.execute_strategy(
            StrategyType.MOMENTUM,
            {'momentum': 0.05}
        )
        self.assertEqual(signal, Signal.HOLD)
        
        # Test case 6: Very strong momentum
        signal = self.engine.execute_strategy(
            StrategyType.MOMENTUM,
            {'momentum': 0.15}
        )
        self.assertEqual(signal, Signal.BUY)
    
    def test_liquidity_provision_comprehensive(self):
        """Comprehensive tests for liquidity provision strategy."""
        self.engine.register_strategy(
            StrategyType.LIQUIDITY_PROVISION,
            {'min_fee_rate': 0.003}
        )
        
        # Test case 1: Good fee rate and liquidity
        signal = self.engine.execute_strategy(
            StrategyType.LIQUIDITY_PROVISION,
            {'fee_rate': 0.005, 'liquidity': 1000000}
        )
        self.assertEqual(signal, Signal.BUY)
        
        # Test case 2: Low fee rate
        signal = self.engine.execute_strategy(
            StrategyType.LIQUIDITY_PROVISION,
            {'fee_rate': 0.001, 'liquidity': 1000000}
        )
        self.assertEqual(signal, Signal.HOLD)
        
        # Test case 3: At threshold
        signal = self.engine.execute_strategy(
            StrategyType.LIQUIDITY_PROVISION,
            {'fee_rate': 0.003, 'liquidity': 1000000}
        )
        self.assertEqual(signal, Signal.HOLD)
        
        # Test case 4: Zero liquidity
        signal = self.engine.execute_strategy(
            StrategyType.LIQUIDITY_PROVISION,
            {'fee_rate': 0.005, 'liquidity': 0}
        )
        self.assertEqual(signal, Signal.HOLD)
        
        # Test case 5: High fee rate
        signal = self.engine.execute_strategy(
            StrategyType.LIQUIDITY_PROVISION,
            {'fee_rate': 0.01, 'liquidity': 5000000}
        )
        self.assertEqual(signal, Signal.BUY)
        
        # Test case 6: Missing data
        signal = self.engine.execute_strategy(
            StrategyType.LIQUIDITY_PROVISION,
            {}
        )
        self.assertEqual(signal, Signal.HOLD)
    
    def test_strategy_with_missing_data(self):
        """Test strategies handle missing market data gracefully."""
        for strategy_type in [
            StrategyType.ARBITRAGE,
            StrategyType.TREND_FOLLOWING,
            StrategyType.MEAN_REVERSION,
            StrategyType.MOMENTUM,
            StrategyType.LIQUIDITY_PROVISION
        ]:
            self.engine.register_strategy(strategy_type, {})
            
            # Should return HOLD when data is missing
            signal = self.engine.execute_strategy(strategy_type, {})
            self.assertEqual(signal, Signal.HOLD)
    
    def test_strategy_performance_tracking(self):
        """Test strategy performance tracking."""
        self.engine.register_strategy(
            StrategyType.ARBITRAGE,
            {'threshold': 0.01}
        )
        
        # Execute strategy
        self.engine.execute_strategy(
            StrategyType.ARBITRAGE,
            {'price_difference': 0.02}
        )
        
        # Get performance
        perf = self.engine.get_strategy_performance(StrategyType.ARBITRAGE)
        
        self.assertIn('total_profit', perf)
        self.assertIn('trades', perf)
        self.assertIn('win_rate', perf)
    
    def test_multiple_strategies_simultaneously(self):
        """Test using multiple strategies in same engine."""
        # Register all strategies
        self.engine.register_strategy(StrategyType.ARBITRAGE, {'threshold': 0.01})
        self.engine.register_strategy(StrategyType.TREND_FOLLOWING, {'min_strength': 0.5})
        self.engine.register_strategy(StrategyType.MOMENTUM, {'momentum_threshold': 0.05})
        
        market_data = {
            'price_difference': 0.02,
            'trend': 0.05,
            'trend_strength': 0.7,
            'momentum': 0.08
        }
        
        # Each strategy should work independently
        arb_signal = self.engine.execute_strategy(StrategyType.ARBITRAGE, market_data)
        trend_signal = self.engine.execute_strategy(StrategyType.TREND_FOLLOWING, market_data)
        momentum_signal = self.engine.execute_strategy(StrategyType.MOMENTUM, market_data)
        
        # All should generate BUY signals with this data
        self.assertEqual(arb_signal, Signal.BUY)
        self.assertEqual(trend_signal, Signal.BUY)
        self.assertEqual(momentum_signal, Signal.BUY)


class TestStrategyEdgeCases(unittest.TestCase):
    """Test edge cases for trading strategies."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = StrategyEngine()
    
    def test_disabled_strategy(self):
        """Test disabled strategy returns HOLD."""
        self.engine.register_strategy(
            StrategyType.ARBITRAGE,
            {'threshold': 0.01}
        )
        
        # Disable strategy
        self.engine.active_strategies['arbitrage']['enabled'] = False
        
        signal = self.engine.execute_strategy(
            StrategyType.ARBITRAGE,
            {'price_difference': 0.05}
        )
        
        self.assertEqual(signal, Signal.HOLD)
    
    def test_strategy_parameter_variations(self):
        """Test strategies with different parameter values."""
        # Test arbitrage with different thresholds
        for threshold in [0.005, 0.01, 0.02, 0.05]:
            engine = StrategyEngine()
            engine.register_strategy(
                StrategyType.ARBITRAGE,
                {'threshold': threshold}
            )
            
            signal = engine.execute_strategy(
                StrategyType.ARBITRAGE,
                {'price_difference': 0.015}
            )
            
            # Signal depends on threshold
            if threshold < 0.015:
                self.assertEqual(signal, Signal.BUY)
            else:
                self.assertEqual(signal, Signal.HOLD)
    
    def test_extreme_values(self):
        """Test strategies with extreme input values."""
        self.engine.register_strategy(
            StrategyType.MOMENTUM,
            {'momentum_threshold': 0.05}
        )
        
        # Test with very large momentum
        signal = self.engine.execute_strategy(
            StrategyType.MOMENTUM,
            {'momentum': 100.0}
        )
        self.assertEqual(signal, Signal.BUY)
        
        # Test with very negative momentum
        signal = self.engine.execute_strategy(
            StrategyType.MOMENTUM,
            {'momentum': -100.0}
        )
        self.assertEqual(signal, Signal.SELL)
    
    def test_strategy_optimization(self):
        """Test strategy optimization disables underperforming strategies."""
        self.engine.register_strategy(
            StrategyType.ARBITRAGE,
            {'threshold': 0.01}
        )
        
        # Simulate poor performance
        self.engine.active_strategies['arbitrage']['performance'] = {
            'total_profit': -100,
            'trades': 20,
            'win_rate': 0.2
        }
        
        # Run optimization
        self.engine.optimize_strategies()
        
        # Should be disabled
        self.assertFalse(self.engine.active_strategies['arbitrage']['enabled'])


if __name__ == '__main__':
    unittest.main()
