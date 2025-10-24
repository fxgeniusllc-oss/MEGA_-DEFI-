"""Tests for Risk Manager."""

import unittest
from mega_defi.core.risk_manager import RiskManager, RiskLevel


class TestRiskManager(unittest.TestCase):
    """Test cases for Risk Manager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.risk_manager = RiskManager(max_portfolio_risk=0.02, max_position_size=0.1)
    
    def test_initialization(self):
        """Test risk manager initialization."""
        self.assertEqual(self.risk_manager.max_portfolio_risk, 0.02)
        self.assertEqual(self.risk_manager.max_position_size, 0.1)
        self.assertEqual(self.risk_manager.total_exposure, 0)
    
    def test_risk_assessment(self):
        """Test risk assessment."""
        market_data = {
            'volatility': 0.03,
            'liquidity': 5000000,
            'trend_strength': 0.6
        }
        
        assessment = self.risk_manager.assess_risk(market_data, 'arbitrage')
        
        self.assertIn('risk_level', assessment)
        self.assertIn('position_size', assessment)
        self.assertIn('stop_loss', assessment)
        self.assertIn('take_profit', assessment)
        self.assertIn('approved', assessment)
    
    def test_risk_level_calculation(self):
        """Test risk level calculation."""
        # Low risk scenario
        low_risk_data = {
            'volatility': 0.01,
            'liquidity': 10000000,
            'trend_strength': 0.5
        }
        assessment = self.risk_manager.assess_risk(low_risk_data, 'arbitrage')
        self.assertEqual(assessment['risk_level'], RiskLevel.LOW)
        
        # High risk scenario
        high_risk_data = {
            'volatility': 0.15,
            'liquidity': 50000,
            'trend_strength': 0.5
        }
        assessment = self.risk_manager.assess_risk(high_risk_data, 'arbitrage')
        self.assertIn(assessment['risk_level'], [RiskLevel.HIGH, RiskLevel.EXTREME])
    
    def test_position_sizing(self):
        """Test position size calculation."""
        market_data = {
            'volatility': 0.02,
            'liquidity': 5000000,
            'trend_strength': 0.5
        }
        
        assessment = self.risk_manager.assess_risk(market_data, 'arbitrage')
        position_size = assessment['position_size']
        
        # Position size should be positive and not exceed max
        self.assertGreaterEqual(position_size, 0)
        self.assertLessEqual(position_size, self.risk_manager.max_position_size)
    
    def test_exposure_management(self):
        """Test exposure management."""
        self.risk_manager.open_position('pos1', {'size': 0.1})
        self.assertAlmostEqual(self.risk_manager.total_exposure, 0.1)
        
        self.risk_manager.open_position('pos2', {'size': 0.2})
        self.assertAlmostEqual(self.risk_manager.total_exposure, 0.3)
        
        self.risk_manager.close_position('pos1')
        self.assertAlmostEqual(self.risk_manager.total_exposure, 0.2)
    
    def test_portfolio_status(self):
        """Test portfolio status reporting."""
        self.risk_manager.update_portfolio(10000)
        status = self.risk_manager.get_portfolio_status()
        
        self.assertEqual(status['portfolio_value'], 10000)
        self.assertEqual(status['total_exposure'], 0)
        self.assertEqual(status['available_capacity'], 1.0)


if __name__ == '__main__':
    unittest.main()
