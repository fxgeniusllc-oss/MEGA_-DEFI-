"""Tests for Market Analyzer."""

import unittest
from mega_defi.core.market_analyzer import MarketAnalyzer


class TestMarketAnalyzer(unittest.TestCase):
    """Test cases for Market Analyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = MarketAnalyzer()
    
    def test_initialization(self):
        """Test market analyzer initialization."""
        self.assertIsInstance(self.analyzer.price_history, list)
        self.assertIsInstance(self.analyzer.volume_history, list)
        self.assertEqual(len(self.analyzer.price_history), 0)
    
    def test_analyze_market(self):
        """Test market analysis."""
        market_data = {
            'price': 100,
            'volume': 1000000,
            'liquidity': 5000000
        }
        
        analysis = self.analyzer.analyze_market(market_data)
        
        self.assertIn('timestamp', analysis)
        self.assertIn('price', analysis)
        self.assertIn('trend', analysis)
        self.assertIn('volatility', analysis)
        self.assertIn('momentum', analysis)
        self.assertIn('opportunities', analysis)
        
        self.assertEqual(analysis['price'], 100)
    
    def test_trend_calculation(self):
        """Test trend calculation with multiple data points."""
        # Add increasing prices
        for i in range(10):
            self.analyzer.analyze_market({'price': 100 + i, 'volume': 1000000, 'liquidity': 5000000})
        
        analysis = self.analyzer.analyze_market({'price': 110, 'volume': 1000000, 'liquidity': 5000000})
        
        # Trend should be positive with increasing prices
        self.assertGreater(analysis['trend'], 0)
    
    def test_opportunity_identification(self):
        """Test opportunity identification."""
        # Build price history
        for i in range(20):
            self.analyzer.analyze_market({'price': 100, 'volume': 1000000, 'liquidity': 5000000})
        
        # Market with arbitrage opportunity
        market_data = {
            'price': 100,
            'volume': 1000000,
            'liquidity': 5000000,
            'exchanges': [
                {'price': 100},
                {'price': 102}
            ]
        }
        
        analysis = self.analyzer.analyze_market(market_data)
        
        # Should identify arbitrage opportunity
        opportunities = analysis['opportunities']
        arbitrage_ops = [op for op in opportunities if op['type'] == 'arbitrage']
        self.assertGreater(len(arbitrage_ops), 0)
    
    def test_market_summary(self):
        """Test market summary generation."""
        # Add some data
        for i in range(5):
            self.analyzer.analyze_market({'price': 100 + i, 'volume': 1000000, 'liquidity': 5000000})
        
        summary = self.analyzer.get_market_summary()
        
        self.assertIn('current_price', summary)
        self.assertIn('price_change_24h', summary)
        self.assertIn('data_points', summary)
        self.assertEqual(summary['data_points'], 5)


if __name__ == '__main__':
    unittest.main()
