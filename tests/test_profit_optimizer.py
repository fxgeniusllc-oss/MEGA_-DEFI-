"""Tests for Profit Optimizer."""

import unittest
from mega_defi.core.profit_optimizer import ProfitOptimizer


class TestProfitOptimizer(unittest.TestCase):
    """Test cases for Profit Optimizer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.optimizer = ProfitOptimizer()
    
    def test_initialization(self):
        """Test profit optimizer initialization."""
        self.assertEqual(self.optimizer.total_profit, 0)
        self.assertEqual(self.optimizer.total_trades, 0)
        self.assertIsInstance(self.optimizer.strategy_performance, dict)
    
    def test_optimize_execution(self):
        """Test execution optimization."""
        market_analysis = {
            'price': 100,
            'volatility': 0.02,
            'trend': 0.05,
            'trend_strength': 0.6,
            'momentum': 0.03,
            'opportunities': []
        }
        
        available_strategies = ['arbitrage', 'trend_following', 'momentum']
        risk_assessment = {'position_size': 0.1}
        
        optimization = self.optimizer.optimize_execution(
            market_analysis,
            available_strategies,
            risk_assessment
        )
        
        self.assertIn('recommended_strategy', optimization)
        self.assertIn('entry_price', optimization)
        self.assertIn('exit_price', optimization)
        self.assertIn('expected_profit', optimization)
        self.assertIn('confidence', optimization)
    
    def test_strategy_selection(self):
        """Test optimal strategy selection."""
        # Market with strong arbitrage opportunity
        market_analysis = {
            'price': 100,
            'volatility': 0.02,
            'trend': 0,
            'trend_strength': 0.1,
            'momentum': 0,
            'price_deviation': 0,
            'liquidity': 1000000,
            'opportunities': [
                {'type': 'arbitrage', 'profit_potential': 0.02},
                {'type': 'arbitrage', 'profit_potential': 0.015}
            ]
        }
        
        strategies = ['arbitrage', 'trend_following', 'momentum']
        risk_assessment = {'position_size': 0.1}
        
        optimization = self.optimizer.optimize_execution(
            market_analysis,
            strategies,
            risk_assessment
        )
        
        # Should select arbitrage for strong arbitrage opportunity
        self.assertEqual(optimization['recommended_strategy'], 'arbitrage')
    
    def test_trade_result_recording(self):
        """Test trade result recording."""
        self.optimizer.record_trade_result('arbitrage', 0.05, True)
        
        self.assertEqual(self.optimizer.total_trades, 1)
        self.assertEqual(self.optimizer.total_profit, 0.05)
        self.assertIn('arbitrage', self.optimizer.strategy_performance)
        
        perf = self.optimizer.strategy_performance['arbitrage']
        self.assertEqual(perf['trades'], 1)
        self.assertEqual(perf['wins'], 1)
        self.assertEqual(perf['win_rate'], 1.0)
    
    def test_performance_report(self):
        """Test performance report generation."""
        # Record some trades
        self.optimizer.record_trade_result('arbitrage', 0.05, True)
        self.optimizer.record_trade_result('trend_following', -0.02, False)
        self.optimizer.record_trade_result('arbitrage', 0.03, True)
        
        report = self.optimizer.get_performance_report()
        
        self.assertEqual(report['total_trades'], 3)
        self.assertEqual(report['total_profit'], 0.06)
        self.assertIn('strategy_performance', report)
        self.assertIn('best_strategy', report)
        self.assertEqual(report['best_strategy'], 'arbitrage')
    
    def test_win_rate_calculation(self):
        """Test overall win rate calculation."""
        self.optimizer.record_trade_result('arbitrage', 0.05, True)
        self.optimizer.record_trade_result('arbitrage', -0.02, False)
        self.optimizer.record_trade_result('momentum', 0.03, True)
        
        report = self.optimizer.get_performance_report()
        
        # 2 wins out of 3 trades = 66.67%
        self.assertAlmostEqual(report['overall_win_rate'], 2/3, places=2)


if __name__ == '__main__':
    unittest.main()
