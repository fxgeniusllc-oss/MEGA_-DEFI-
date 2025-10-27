"""Comprehensive edge case tests for all core modules."""

import unittest
from mega_defi.core.market_analyzer import MarketAnalyzer
from mega_defi.core.risk_manager import RiskManager, RiskLevel
from mega_defi.core.profit_optimizer import ProfitOptimizer


class TestMarketAnalyzerEdgeCases(unittest.TestCase):
    """Edge case tests for Market Analyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = MarketAnalyzer()
    
    def test_empty_price_history(self):
        """Test analysis with no historical data."""
        market_data = {'price': 100, 'volume': 1000000, 'liquidity': 5000000}
        
        analysis = self.analyzer.analyze_market(market_data)
        
        # Should handle gracefully
        self.assertEqual(analysis['trend'], 0.0)
        self.assertEqual(analysis['volatility'], 0.0)
        self.assertEqual(analysis['momentum'], 0.0)
    
    def test_extreme_price_spike(self):
        """Test handling of extreme price movement."""
        # Build normal history
        for i in range(20):
            self.analyzer.analyze_market({'price': 100, 'volume': 1000000, 'liquidity': 5000000})
        
        # Add spike to history
        self.analyzer.analyze_market({'price': 1000, 'volume': 1000000, 'liquidity': 5000000})
        
        # Now analyze another point to see the volatility from the spike
        analysis = self.analyzer.analyze_market({'price': 1000, 'volume': 1000000, 'liquidity': 5000000})
        
        # Should detect high volatility after spike is in history
        self.assertGreater(analysis['volatility'], 0.1)
        self.assertGreater(abs(analysis['price_deviation']), 3.0)
    
    def test_zero_price(self):
        """Test handling of zero price."""
        market_data = {'price': 0, 'volume': 1000000, 'liquidity': 5000000}
        
        # Should not crash
        analysis = self.analyzer.analyze_market(market_data)
        self.assertEqual(analysis['price'], 0)
    
    def test_negative_values(self):
        """Test handling of negative values."""
        market_data = {'price': -100, 'volume': -1000, 'liquidity': -5000}
        
        # Should handle gracefully
        analysis = self.analyzer.analyze_market(market_data)
        self.assertIsNotNone(analysis)
    
    def test_very_small_values(self):
        """Test handling of very small price values."""
        for i in range(10):
            self.analyzer.analyze_market({
                'price': 0.0001 + i * 0.00001,
                'volume': 1000,
                'liquidity': 5000
            })
        
        summary = self.analyzer.get_market_summary()
        self.assertGreater(summary['current_price'], 0)
    
    def test_large_price_history(self):
        """Test with maximum price history."""
        # Add more than 1000 data points
        for i in range(1200):
            self.analyzer.analyze_market({'price': 100 + i * 0.01, 'volume': 1000000, 'liquidity': 5000000})
        
        # Should keep only last 1000
        self.assertEqual(len(self.analyzer.price_history), 1000)
        self.assertEqual(len(self.analyzer.volume_history), 1000)
    
    def test_rapid_price_changes(self):
        """Test rapid alternating price changes."""
        prices = [100, 110, 95, 115, 90, 120, 85]
        
        for price in prices:
            self.analyzer.analyze_market({'price': price, 'volume': 1000000, 'liquidity': 5000000})
        
        analysis = self.analyzer.analyze_market({'price': 100, 'volume': 1000000, 'liquidity': 5000000})
        
        # Should detect high volatility
        self.assertGreater(analysis['volatility'], 0.05)
    
    def test_constant_price(self):
        """Test with constant price (no movement)."""
        for i in range(20):
            self.analyzer.analyze_market({'price': 100, 'volume': 1000000, 'liquidity': 5000000})
        
        analysis = self.analyzer.analyze_market({'price': 100, 'volume': 1000000, 'liquidity': 5000000})
        
        # Trend and volatility should be near zero
        self.assertAlmostEqual(analysis['trend'], 0.0, places=5)
        self.assertAlmostEqual(analysis['volatility'], 0.0, places=5)
    
    def test_missing_exchange_data(self):
        """Test opportunity identification without exchange data."""
        market_data = {'price': 100, 'volume': 1000000, 'liquidity': 5000000}
        
        # Build history
        for i in range(20):
            self.analyzer.analyze_market(market_data)
        
        analysis = self.analyzer.analyze_market(market_data)
        
        # Should still work, just won't find arbitrage opportunities
        self.assertIsInstance(analysis['opportunities'], list)
    
    def test_single_exchange(self):
        """Test with only one exchange."""
        market_data = {
            'price': 100,
            'volume': 1000000,
            'liquidity': 5000000,
            'exchanges': [{'price': 100}]
        }
        
        # Build history
        for i in range(20):
            self.analyzer.analyze_market(market_data)
        
        analysis = self.analyzer.analyze_market(market_data)
        
        # No arbitrage opportunity with single exchange
        arbitrage_ops = [op for op in analysis['opportunities'] if op['type'] == 'arbitrage']
        self.assertEqual(len(arbitrage_ops), 0)


class TestRiskManagerEdgeCases(unittest.TestCase):
    """Edge case tests for Risk Manager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.risk_manager = RiskManager(max_portfolio_risk=0.02, max_position_size=0.1)
        self.risk_manager.update_portfolio(10000)
    
    def test_extreme_volatility(self):
        """Test with extreme volatility."""
        market_data = {
            'volatility': 0.5,  # 50% volatility
            'liquidity': 5000000,
            'trend_strength': 0.5
        }
        
        assessment = self.risk_manager.assess_risk(market_data, 'arbitrage')
        
        # Should classify as high or extreme risk (50% volatility gives high)
        self.assertIn(assessment['risk_level'], [RiskLevel.HIGH, RiskLevel.EXTREME])
        
        # Position size should be very small
        self.assertLess(assessment['position_size'], 0.05)
    
    def test_zero_liquidity(self):
        """Test with zero liquidity."""
        market_data = {
            'volatility': 0.02,
            'liquidity': 0,
            'trend_strength': 0.5
        }
        
        assessment = self.risk_manager.assess_risk(market_data, 'arbitrage')
        
        # Should classify as medium or higher risk (zero liquidity isn't critical by itself)
        self.assertIn(assessment['risk_level'], [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.EXTREME])
    
    def test_maximum_exposure_limit(self):
        """Test behavior at maximum exposure."""
        # Open positions up to 80% exposure
        for i in range(8):
            self.risk_manager.open_position(f'pos{i}', {'size': 0.1})
        
        # Try to assess another trade
        market_data = {
            'volatility': 0.02,
            'liquidity': 5000000,
            'trend_strength': 0.5
        }
        
        assessment = self.risk_manager.assess_risk(market_data, 'arbitrage')
        
        # Should not approve due to exposure limit
        self.assertFalse(assessment['approved'])
    
    def test_position_size_with_high_exposure(self):
        """Test position sizing adjusts with existing exposure."""
        # Open some positions
        self.risk_manager.open_position('pos1', {'size': 0.3})
        
        market_data = {
            'volatility': 0.02,
            'liquidity': 5000000,
            'trend_strength': 0.5
        }
        
        assessment = self.risk_manager.assess_risk(market_data, 'arbitrage')
        
        # Remaining capacity should affect position size
        self.assertLessEqual(assessment['position_size'], 0.7)
    
    def test_close_nonexistent_position(self):
        """Test closing position that doesn't exist."""
        # Should handle gracefully
        self.risk_manager.close_position('nonexistent')
        
        # Exposure should remain unchanged
        self.assertEqual(self.risk_manager.total_exposure, 0)
    
    def test_negative_exposure_prevention(self):
        """Test that exposure never goes negative."""
        self.risk_manager.open_position('pos1', {'size': 0.1})
        
        # Try to close multiple times
        self.risk_manager.close_position('pos1')
        self.risk_manager.close_position('pos1')
        
        # Should not go negative
        self.assertGreaterEqual(self.risk_manager.total_exposure, 0)
    
    def test_zero_portfolio_value(self):
        """Test with zero portfolio value."""
        self.risk_manager.update_portfolio(0)
        
        status = self.risk_manager.get_portfolio_status()
        self.assertEqual(status['portfolio_value'], 0)
    
    def test_very_low_risk_scenario(self):
        """Test optimal conditions."""
        market_data = {
            'volatility': 0.005,  # Very low
            'liquidity': 50000000,  # Very high
            'trend_strength': 0.5
        }
        
        assessment = self.risk_manager.assess_risk(market_data, 'arbitrage')
        
        # Should be low risk
        self.assertEqual(assessment['risk_level'], RiskLevel.LOW)
        
        # Should allow full position size
        self.assertAlmostEqual(assessment['position_size'], self.risk_manager.max_position_size, places=2)
    
    def test_stop_loss_limits(self):
        """Test stop loss doesn't exceed maximum."""
        market_data = {
            'volatility': 1.0,  # Extreme volatility
            'liquidity': 5000000,
            'trend_strength': 0.5
        }
        
        assessment = self.risk_manager.assess_risk(market_data, 'trend_following')
        
        # Stop loss should not exceed 10%
        self.assertLessEqual(assessment['stop_loss'], 0.1)
    
    def test_take_profit_limits(self):
        """Test take profit doesn't exceed maximum."""
        market_data = {
            'volatility': 1.0,
            'liquidity': 5000000,
            'trend_strength': 0.5
        }
        
        assessment = self.risk_manager.assess_risk(market_data, 'trend_following')
        
        # Take profit should not exceed 25%
        self.assertLessEqual(assessment['take_profit'], 0.25)
    
    def test_risk_reward_ratio(self):
        """Test risk-reward ratio is favorable."""
        market_data = {
            'volatility': 0.02,
            'liquidity': 5000000,
            'trend_strength': 0.5
        }
        
        assessment = self.risk_manager.assess_risk(market_data, 'arbitrage')
        
        # Risk-reward should be positive
        self.assertGreater(assessment['risk_reward_ratio'], 0)


class TestProfitOptimizerEdgeCases(unittest.TestCase):
    """Edge case tests for Profit Optimizer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.optimizer = ProfitOptimizer()
    
    def test_zero_trades(self):
        """Test performance report with zero trades."""
        report = self.optimizer.get_performance_report()
        
        self.assertEqual(report['total_trades'], 0)
        self.assertEqual(report['total_profit'], 0)
        self.assertEqual(report['average_profit_per_trade'], 0)
        self.assertIsNone(report['best_strategy'])
    
    def test_all_losing_trades(self):
        """Test with all losing trades."""
        for i in range(10):
            self.optimizer.record_trade_result('arbitrage', -0.01, False)
        
        report = self.optimizer.get_performance_report()
        
        self.assertEqual(report['total_trades'], 10)
        self.assertLess(report['total_profit'], 0)
        self.assertEqual(report['overall_win_rate'], 0.0)
    
    def test_all_winning_trades(self):
        """Test with all winning trades."""
        for i in range(10):
            self.optimizer.record_trade_result('arbitrage', 0.02, True)
        
        report = self.optimizer.get_performance_report()
        
        self.assertEqual(report['total_trades'], 10)
        self.assertGreater(report['total_profit'], 0)
        self.assertEqual(report['overall_win_rate'], 1.0)
    
    def test_mixed_strategy_performance(self):
        """Test with multiple strategies having different performance."""
        # Good strategy
        for i in range(5):
            self.optimizer.record_trade_result('arbitrage', 0.03, True)
        
        # Poor strategy
        for i in range(5):
            self.optimizer.record_trade_result('trend_following', -0.01, False)
        
        report = self.optimizer.get_performance_report()
        
        # Best strategy should be arbitrage
        self.assertEqual(report['best_strategy'], 'arbitrage')
    
    def test_optimize_with_no_opportunities(self):
        """Test optimization with no market opportunities."""
        market_analysis = {
            'price': 100,
            'volatility': 0.02,
            'trend': 0,
            'trend_strength': 0,
            'momentum': 0,
            'price_deviation': 0,
            'liquidity': 1000000,
            'opportunities': []
        }
        
        optimization = self.optimizer.optimize_execution(
            market_analysis,
            ['arbitrage', 'trend_following'],
            {'position_size': 0.1}
        )
        
        # Should still provide recommendation
        self.assertIn('recommended_strategy', optimization)
        self.assertIn('expected_profit', optimization)
    
    def test_optimize_with_single_strategy(self):
        """Test optimization with only one strategy available."""
        market_analysis = {
            'price': 100,
            'volatility': 0.02,
            'trend': 0.05,
            'trend_strength': 0.6,
            'momentum': 0.03,
            'opportunities': []
        }
        
        optimization = self.optimizer.optimize_execution(
            market_analysis,
            ['momentum'],
            {'position_size': 0.1}
        )
        
        # Should select the only available strategy
        self.assertEqual(optimization['recommended_strategy'], 'momentum')
    
    def test_confidence_bounds(self):
        """Test confidence stays within 0-1 bounds."""
        market_analysis = {
            'price': 100,
            'volatility': 0.02,
            'trend': 0.1,
            'trend_strength': 1.0,
            'momentum': 0.1,
            'opportunities': [
                {'type': 'arbitrage', 'profit_potential': 0.05},
                {'type': 'momentum', 'profit_potential': 0.03},
                {'type': 'trend', 'profit_potential': 0.04}
            ]
        }
        
        optimization = self.optimizer.optimize_execution(
            market_analysis,
            ['arbitrage', 'trend_following', 'momentum'],
            {'position_size': 0.1}
        )
        
        # Confidence should be between 0 and 1
        self.assertGreaterEqual(optimization['confidence'], 0)
        self.assertLessEqual(optimization['confidence'], 1.0)
    
    def test_strategy_selection_with_no_historical_data(self):
        """Test strategy selection with no performance history."""
        market_analysis = {
            'price': 100,
            'volatility': 0.02,
            'trend': 0.05,
            'trend_strength': 0.7,
            'momentum': 0.03,
            'opportunities': []
        }
        
        optimization = self.optimizer.optimize_execution(
            market_analysis,
            ['arbitrage', 'trend_following', 'momentum'],
            {'position_size': 0.1}
        )
        
        # Should still select a strategy
        self.assertIn(optimization['recommended_strategy'], 
                     ['arbitrage', 'trend_following', 'momentum'])
    
    def test_large_profit_recording(self):
        """Test recording very large profit."""
        self.optimizer.record_trade_result('arbitrage', 10.0, True)
        
        report = self.optimizer.get_performance_report()
        
        self.assertEqual(report['total_profit'], 10.0)
        self.assertEqual(report['total_trades'], 1)
    
    def test_large_loss_recording(self):
        """Test recording very large loss."""
        self.optimizer.record_trade_result('arbitrage', -5.0, False)
        
        report = self.optimizer.get_performance_report()
        
        self.assertEqual(report['total_profit'], -5.0)
        self.assertEqual(report['overall_win_rate'], 0.0)


if __name__ == '__main__':
    unittest.main()
