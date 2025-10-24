"""Tests for Strategy Engine."""

import unittest
from mega_defi.core.strategy_engine import StrategyEngine, StrategyType, Signal


class TestStrategyEngine(unittest.TestCase):
    """Test cases for Strategy Engine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = StrategyEngine()
    
    def test_initialization(self):
        """Test strategy engine initialization."""
        self.assertIsInstance(self.engine.active_strategies, dict)
        self.assertEqual(len(self.engine.active_strategies), 0)
    
    def test_register_strategy(self):
        """Test strategy registration."""
        self.engine.register_strategy(
            StrategyType.ARBITRAGE,
            {'threshold': 0.01}
        )
        self.assertIn('arbitrage', self.engine.active_strategies)
        self.assertTrue(self.engine.active_strategies['arbitrage']['enabled'])
    
    def test_arbitrage_strategy(self):
        """Test arbitrage strategy execution."""
        self.engine.register_strategy(
            StrategyType.ARBITRAGE,
            {'threshold': 0.01}
        )
        
        # Test with price difference above threshold
        market_data = {'price_difference': 0.02}
        signal = self.engine.execute_strategy(StrategyType.ARBITRAGE, market_data)
        self.assertEqual(signal, Signal.BUY)
        
        # Test with negative price difference
        market_data = {'price_difference': -0.02}
        signal = self.engine.execute_strategy(StrategyType.ARBITRAGE, market_data)
        self.assertEqual(signal, Signal.SELL)
        
        # Test with no significant difference
        market_data = {'price_difference': 0.005}
        signal = self.engine.execute_strategy(StrategyType.ARBITRAGE, market_data)
        self.assertEqual(signal, Signal.HOLD)
    
    def test_trend_following_strategy(self):
        """Test trend following strategy execution."""
        self.engine.register_strategy(
            StrategyType.TREND_FOLLOWING,
            {'min_strength': 0.5}
        )
        
        # Test with strong uptrend
        market_data = {'trend': 0.1, 'trend_strength': 0.6}
        signal = self.engine.execute_strategy(StrategyType.TREND_FOLLOWING, market_data)
        self.assertEqual(signal, Signal.BUY)
        
        # Test with strong downtrend
        market_data = {'trend': -0.1, 'trend_strength': 0.6}
        signal = self.engine.execute_strategy(StrategyType.TREND_FOLLOWING, market_data)
        self.assertEqual(signal, Signal.SELL)
        
        # Test with weak trend
        market_data = {'trend': 0.1, 'trend_strength': 0.3}
        signal = self.engine.execute_strategy(StrategyType.TREND_FOLLOWING, market_data)
        self.assertEqual(signal, Signal.HOLD)
    
    def test_mean_reversion_strategy(self):
        """Test mean reversion strategy execution."""
        self.engine.register_strategy(
            StrategyType.MEAN_REVERSION,
            {'deviation_threshold': 2.0}
        )
        
        # Test with high positive deviation
        market_data = {'price_deviation': 2.5}
        signal = self.engine.execute_strategy(StrategyType.MEAN_REVERSION, market_data)
        self.assertEqual(signal, Signal.SELL)
        
        # Test with high negative deviation
        market_data = {'price_deviation': -2.5}
        signal = self.engine.execute_strategy(StrategyType.MEAN_REVERSION, market_data)
        self.assertEqual(signal, Signal.BUY)
    
    def test_unregistered_strategy(self):
        """Test execution of unregistered strategy."""
        signal = self.engine.execute_strategy(StrategyType.ARBITRAGE, {})
        self.assertEqual(signal, Signal.HOLD)


if __name__ == '__main__':
    unittest.main()
