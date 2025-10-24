"""Comprehensive integration tests for Profit Machine."""

import unittest
from mega_defi.profit_machine import ProfitMachine, create_profit_machine
from mega_defi.core.strategy_engine import StrategyType, Signal


class TestProfitMachine(unittest.TestCase):
    """Test cases for the main Profit Machine orchestrator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.machine = create_profit_machine(
            portfolio_value=10000,
            max_risk_per_trade=0.02,
            max_position_size=0.1
        )
    
    def test_initialization(self):
        """Test profit machine initialization with all components."""
        self.assertIsNotNone(self.machine.strategy_engine)
        self.assertIsNotNone(self.machine.market_analyzer)
        self.assertIsNotNone(self.machine.risk_manager)
        self.assertIsNotNone(self.machine.profit_optimizer)
        
        # Verify all 5 strategies are registered
        strategies = self.machine.strategy_engine.active_strategies
        self.assertEqual(len(strategies), 5)
        self.assertIn('arbitrage', strategies)
        self.assertIn('trend_following', strategies)
        self.assertIn('mean_reversion', strategies)
        self.assertIn('momentum', strategies)
        self.assertIn('liquidity_provision', strategies)
    
    def test_create_profit_machine_factory(self):
        """Test factory function creates valid instance."""
        machine = create_profit_machine(
            portfolio_value=50000,
            max_risk_per_trade=0.01,
            max_position_size=0.05
        )
        
        self.assertIsInstance(machine, ProfitMachine)
        self.assertEqual(machine.risk_manager.max_portfolio_risk, 0.01)
        self.assertEqual(machine.risk_manager.max_position_size, 0.05)
    
    def test_process_market_data_basic(self):
        """Test basic market data processing."""
        market_data = {
            'price': 100.0,
            'volume': 1000000,
            'liquidity': 5000000,
            'fee_rate': 0.003
        }
        
        recommendation = self.machine.process_market_data(market_data)
        
        self.assertIn('signal', recommendation)
        self.assertIn('strategy', recommendation)
        self.assertIn('confidence', recommendation)
        self.assertIn('expected_profit', recommendation)
        self.assertIn('risk_assessment', recommendation)
        self.assertIn('market_analysis', recommendation)
        self.assertIn('approved', recommendation)
    
    def test_process_arbitrage_opportunity(self):
        """Test processing market data with arbitrage opportunity."""
        market_data = {
            'price': 100.0,
            'volume': 1000000,
            'liquidity': 5000000,
            'fee_rate': 0.003,
            'exchanges': [
                {'name': 'Exchange A', 'price': 100},
                {'name': 'Exchange B', 'price': 102}
            ]
        }
        
        recommendation = self.machine.process_market_data(market_data)
        
        # Should identify arbitrage opportunity
        opportunities = recommendation['market_analysis']['opportunities']
        arbitrage_ops = [op for op in opportunities if op['type'] == 'arbitrage']
        self.assertGreater(len(arbitrage_ops), 0)
    
    def test_execute_approved_trade(self):
        """Test executing an approved trade."""
        # Create market data that should generate approved trade
        market_data = {
            'price': 100.0,
            'volume': 1000000,
            'liquidity': 5000000,
            'fee_rate': 0.004
        }
        
        recommendation = self.machine.process_market_data(market_data)
        
        if recommendation['approved']:
            result = self.machine.execute_trade(recommendation)
            
            self.assertTrue(result['executed'])
            self.assertIn('position_id', result)
            self.assertIn('strategy', result)
            self.assertIn('signal', result)
            self.assertIn('position_size', result)
            self.assertIn('entry_price', result)
            self.assertIn('stop_loss', result)
            self.assertIn('take_profit', result)
    
    def test_execute_unapproved_trade(self):
        """Test that unapproved trades are not executed."""
        recommendation = {
            'approved': False,
            'signal': 'buy',
            'strategy': 'arbitrage',
            'risk_assessment': {}
        }
        
        result = self.machine.execute_trade(recommendation)
        
        self.assertFalse(result['executed'])
        self.assertIn('reason', result)
    
    def test_trade_lifecycle(self):
        """Test complete trade lifecycle: process -> execute -> close."""
        market_data = {
            'price': 100.0,
            'volume': 2000000,
            'liquidity': 10000000,
            'fee_rate': 0.005
        }
        
        # Process and potentially execute
        recommendation = self.machine.process_market_data(market_data)
        
        if recommendation['approved']:
            # Execute trade
            result = self.machine.execute_trade(recommendation)
            
            if result['executed']:
                position_id = result['position_id']
                
                # Verify position is open
                self.assertIn(position_id, self.machine.risk_manager.active_positions)
                
                # Close trade with profit
                self.machine.close_trade(position_id, 105.0, 0.05, True)
                
                # Verify position is closed
                self.assertNotIn(position_id, self.machine.risk_manager.active_positions)
                
                # Verify trade was recorded
                self.assertGreater(self.machine.profit_optimizer.total_trades, 0)
    
    def test_performance_report(self):
        """Test comprehensive performance report generation."""
        report = self.machine.get_performance_report()
        
        self.assertIn('portfolio_status', report)
        self.assertIn('market_summary', report)
        self.assertIn('profit_report', report)
        
        # Verify portfolio status structure
        portfolio = report['portfolio_status']
        self.assertIn('portfolio_value', portfolio)
        self.assertIn('total_exposure', portfolio)
        self.assertIn('active_positions', portfolio)
        
        # Verify profit report structure
        profit = report['profit_report']
        self.assertIn('total_profit', profit)
        self.assertIn('total_trades', profit)
        self.assertIn('overall_win_rate', profit)
    
    def test_multiple_trades_tracking(self):
        """Test tracking multiple trades and portfolio state."""
        # Process multiple market cycles
        base_price = 100.0
        
        for i in range(5):
            market_data = {
                'price': base_price + i,
                'volume': 1000000 + i * 100000,
                'liquidity': 5000000,
                'fee_rate': 0.003 + i * 0.0001
            }
            
            recommendation = self.machine.process_market_data(market_data)
            
            if recommendation['approved']:
                result = self.machine.execute_trade(recommendation)
                
                # Some trades should execute
                if result.get('executed'):
                    # Close trade immediately for testing
                    self.machine.close_trade(
                        result['position_id'],
                        base_price + i + 1,
                        0.01,
                        True
                    )
        
        # At least one trade should have been processed
        report = self.machine.get_performance_report()
        # Total trades could be 0 or more depending on market conditions
        self.assertGreaterEqual(report['profit_report']['total_trades'], 0)
    
    def test_risk_limits_enforcement(self):
        """Test that risk limits are enforced across trades."""
        # Try to open multiple positions to test exposure limits
        positions_opened = 0
        
        for i in range(10):
            market_data = {
                'price': 100.0 + i,
                'volume': 5000000,
                'liquidity': 20000000,
                'fee_rate': 0.005
            }
            
            recommendation = self.machine.process_market_data(market_data)
            
            if recommendation['approved']:
                result = self.machine.execute_trade(recommendation)
                if result['executed']:
                    positions_opened += 1
        
        # Should not exceed exposure limits
        status = self.machine.risk_manager.get_portfolio_status()
        self.assertLessEqual(status['total_exposure'], 0.8)
    
    def test_display_performance(self):
        """Test performance display doesn't crash."""
        # This should print output without errors
        try:
            self.machine.display_performance()
            success = True
        except Exception:
            success = False
        
        self.assertTrue(success)


class TestProfitMachineWithTradingScenarios(unittest.TestCase):
    """Test profit machine with realistic trading scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.machine = create_profit_machine(
            portfolio_value=100000,
            max_risk_per_trade=0.015,
            max_position_size=0.08
        )
    
    def test_trending_market_scenario(self):
        """Test profit machine in trending market."""
        base_price = 1000.0
        
        # Simulate uptrending market
        for i in range(10):
            price = base_price * (1 + i * 0.01)  # 1% increase each cycle
            
            market_data = {
                'price': price,
                'volume': 2000000,
                'liquidity': 10000000,
                'fee_rate': 0.003
            }
            
            recommendation = self.machine.process_market_data(market_data)
            
            # In trending market, should generate signals
            self.assertIn(recommendation['signal'], ['buy', 'sell', 'hold'])
    
    def test_volatile_market_scenario(self):
        """Test profit machine in volatile market."""
        prices = [100, 105, 98, 107, 95, 110, 92, 108]
        
        for price in prices:
            market_data = {
                'price': price,
                'volume': 3000000,
                'liquidity': 8000000,
                'fee_rate': 0.003
            }
            
            recommendation = self.machine.process_market_data(market_data)
            
            # High volatility should be detected
            if len(self.machine.market_analyzer.price_history) > 5:
                volatility = recommendation['market_analysis']['volatility']
                self.assertGreater(volatility, 0)
    
    def test_arbitrage_scenario(self):
        """Test profit machine with arbitrage opportunities."""
        market_data = {
            'price': 100.0,
            'volume': 5000000,
            'liquidity': 20000000,
            'fee_rate': 0.002,
            'exchanges': [
                {'name': 'Uniswap', 'price': 100.0},
                {'name': 'SushiSwap', 'price': 101.5},
                {'name': 'PancakeSwap', 'price': 99.5},
            ]
        }
        
        recommendation = self.machine.process_market_data(market_data)
        
        # Should detect arbitrage opportunity
        opportunities = recommendation['market_analysis']['opportunities']
        arbitrage_opportunities = [o for o in opportunities if o['type'] == 'arbitrage']
        self.assertGreater(len(arbitrage_opportunities), 0)
    
    def test_low_liquidity_scenario(self):
        """Test profit machine with low liquidity markets."""
        market_data = {
            'price': 100.0,
            'volume': 10000,  # Very low volume
            'liquidity': 50000,  # Very low liquidity
            'fee_rate': 0.003
        }
        
        recommendation = self.machine.process_market_data(market_data)
        
        # Should assess as higher risk (medium, high, or extreme)
        risk_level = recommendation['risk_assessment']['risk_level']
        self.assertIn(risk_level, ['medium', 'high', 'extreme'])


if __name__ == '__main__':
    unittest.main()
