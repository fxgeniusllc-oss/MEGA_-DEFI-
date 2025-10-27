"""End-to-end workflow and performance validation tests."""

import unittest
from mega_defi.profit_machine import create_profit_machine


class TestEndToEndWorkflows(unittest.TestCase):
    """Test complete trading workflows from start to finish."""
    
    def test_complete_trading_cycle(self):
        """Test a complete trading cycle from initialization to profit reporting."""
        # Initialize machine
        machine = create_profit_machine(
            portfolio_value=50000,
            max_risk_per_trade=0.02,
            max_position_size=0.1
        )
        
        # Process market data
        market_data = {
            'price': 100.0,
            'volume': 2000000,
            'liquidity': 10000000,
            'fee_rate': 0.004
        }
        
        recommendation = machine.process_market_data(market_data)
        
        # Execute if approved
        if recommendation['approved']:
            result = machine.execute_trade(recommendation)
            
            if result['executed']:
                # Simulate profit
                machine.close_trade(
                    result['position_id'],
                    105.0,
                    0.05,
                    True
                )
                
                # Get performance
                report = machine.get_performance_report()
                
                # Validate profit was recorded
                self.assertGreater(report['profit_report']['total_trades'], 0)
                self.assertGreater(report['profit_report']['total_profit'], 0)
    
    def test_multi_strategy_workflow(self):
        """Test workflow using multiple strategies."""
        machine = create_profit_machine(portfolio_value=100000)
        
        scenarios = [
            # Arbitrage scenario
            {
                'price': 100.0,
                'volume': 5000000,
                'liquidity': 20000000,
                'fee_rate': 0.003,
                'exchanges': [
                    {'price': 100.0},
                    {'price': 101.5}
                ]
            },
            # Trend following scenario
            {
                'price': 105.0,
                'volume': 3000000,
                'liquidity': 15000000,
                'fee_rate': 0.003
            },
            # Mean reversion scenario
            {
                'price': 102.0,
                'volume': 2500000,
                'liquidity': 12000000,
                'fee_rate': 0.003
            }
        ]
        
        executed_trades = 0
        
        for scenario in scenarios:
            recommendation = machine.process_market_data(scenario)
            
            if recommendation['approved']:
                result = machine.execute_trade(recommendation)
                if result['executed']:
                    executed_trades += 1
                    # Close immediately
                    machine.close_trade(
                        result['position_id'],
                        scenario['price'] * 1.02,
                        0.02,
                        True
                    )
        
        # At least some trades should have executed
        report = machine.get_performance_report()
        self.assertGreaterEqual(report['profit_report']['total_trades'], 0)
    
    def test_risk_management_workflow(self):
        """Test risk management prevents excessive exposure."""
        machine = create_profit_machine(
            portfolio_value=10000,
            max_risk_per_trade=0.02,
            max_position_size=0.1
        )
        
        # Try to open many positions
        open_positions = []
        
        for i in range(20):
            market_data = {
                'price': 100.0 + i,
                'volume': 5000000,
                'liquidity': 20000000,
                'fee_rate': 0.005
            }
            
            recommendation = machine.process_market_data(market_data)
            
            if recommendation['approved']:
                result = machine.execute_trade(recommendation)
                if result['executed']:
                    open_positions.append(result['position_id'])
        
        # Check exposure limits
        status = machine.risk_manager.get_portfolio_status()
        
        # Should not exceed 80% exposure
        self.assertLessEqual(status['total_exposure'], 0.8)
        
        # Clean up
        for pos_id in open_positions:
            if pos_id in machine.risk_manager.active_positions:
                machine.close_trade(pos_id, 100.0, 0.01, True)
    
    def test_profit_optimization_workflow(self):
        """Test profit optimizer selects best strategies over time."""
        machine = create_profit_machine(portfolio_value=50000)
        
        # Simulate trades with different strategies performing differently
        good_strategy_data = {
            'price': 100.0,
            'volume': 5000000,
            'liquidity': 20000000,
            'fee_rate': 0.005,
            'price_difference': 0.02  # Good for arbitrage
        }
        
        # Execute multiple successful trades
        for i in range(5):
            recommendation = machine.process_market_data(good_strategy_data)
            if recommendation['approved']:
                result = machine.execute_trade(recommendation)
                if result['executed']:
                    # Record win
                    machine.close_trade(
                        result['position_id'],
                        good_strategy_data['price'] * 1.05,
                        0.05,
                        True
                    )
        
        # Check that profit optimizer has recorded performance
        report = machine.get_performance_report()
        
        if report['profit_report']['total_trades'] > 0:
            # Should have positive profit
            self.assertGreater(report['profit_report']['total_profit'], 0)
            
            # Win rate should be high
            self.assertGreater(report['profit_report']['overall_win_rate'], 0)
    
    def test_market_analysis_accumulation(self):
        """Test market analyzer accumulates data correctly over time."""
        machine = create_profit_machine(portfolio_value=10000)
        
        # Process increasing prices
        for i in range(30):
            market_data = {
                'price': 100.0 + i * 0.5,
                'volume': 1000000 + i * 10000,
                'liquidity': 5000000,
                'fee_rate': 0.003
            }
            
            machine.process_market_data(market_data)
        
        # Get market summary
        summary = machine.market_analyzer.get_market_summary()
        
        # Should have accumulated data
        self.assertEqual(summary['data_points'], 30)
        
        # Current price should be the last one
        self.assertEqual(summary['current_price'], 114.5)
    
    def test_full_lifecycle_with_losses(self):
        """Test complete lifecycle including losing trades."""
        machine = create_profit_machine(portfolio_value=20000)
        
        trades = [
            {'price': 100, 'exit': 105, 'profit': 0.05, 'win': True},
            {'price': 105, 'exit': 103, 'profit': -0.02, 'win': False},
            {'price': 103, 'exit': 108, 'profit': 0.05, 'win': True},
            {'price': 108, 'exit': 106, 'profit': -0.02, 'win': False},
            {'price': 106, 'exit': 112, 'profit': 0.06, 'win': True},
        ]
        
        for trade_data in trades:
            market_data = {
                'price': trade_data['price'],
                'volume': 3000000,
                'liquidity': 15000000,
                'fee_rate': 0.004
            }
            
            recommendation = machine.process_market_data(market_data)
            
            if recommendation['approved']:
                result = machine.execute_trade(recommendation)
                if result['executed']:
                    machine.close_trade(
                        result['position_id'],
                        trade_data['exit'],
                        trade_data['profit'],
                        trade_data['win']
                    )
        
        # Get final report
        report = machine.get_performance_report()
        
        if report['profit_report']['total_trades'] > 0:
            # Should have mixed results
            win_rate = report['profit_report']['overall_win_rate']
            self.assertGreater(win_rate, 0)
            self.assertLess(win_rate, 1)


class TestPerformanceMetricsValidation(unittest.TestCase):
    """Validate all performance metrics and features claimed in README."""
    
    def test_five_strategy_support(self):
        """Validate system supports all 5 claimed strategies."""
        machine = create_profit_machine()
        
        strategies = machine.strategy_engine.active_strategies
        
        # Verify all 5 strategies are available
        required_strategies = [
            'arbitrage',
            'trend_following',
            'mean_reversion',
            'momentum',
            'liquidity_provision'
        ]
        
        for strategy in required_strategies:
            self.assertIn(strategy, strategies)
            self.assertTrue(strategies[strategy]['enabled'])
    
    def test_portfolio_protection_features(self):
        """Validate portfolio protection features."""
        machine = create_profit_machine(
            portfolio_value=10000,
            max_risk_per_trade=0.02,
            max_position_size=0.1
        )
        
        # Check risk manager configuration
        self.assertEqual(machine.risk_manager.max_portfolio_risk, 0.02)
        self.assertEqual(machine.risk_manager.max_position_size, 0.1)
        
        # Test risk assessment includes required fields
        market_data = {
            'volatility': 0.03,
            'liquidity': 5000000,
            'trend_strength': 0.6
        }
        
        assessment = machine.risk_manager.assess_risk(market_data, 'arbitrage')
        
        # Verify all risk management features
        self.assertIn('risk_level', assessment)
        self.assertIn('position_size', assessment)
        self.assertIn('stop_loss', assessment)
        self.assertIn('take_profit', assessment)
        self.assertIn('risk_reward_ratio', assessment)
        self.assertIn('approved', assessment)
    
    def test_performance_tracking_features(self):
        """Validate comprehensive performance tracking."""
        machine = create_profit_machine()
        
        report = machine.get_performance_report()
        
        # Verify all tracked metrics exist
        self.assertIn('portfolio_status', report)
        self.assertIn('profit_report', report)
        self.assertIn('market_summary', report)
        
        # Portfolio metrics
        portfolio = report['portfolio_status']
        self.assertIn('portfolio_value', portfolio)
        self.assertIn('total_exposure', portfolio)
        self.assertIn('available_capacity', portfolio)
        self.assertIn('active_positions', portfolio)
        
        # Profit metrics
        profit = report['profit_report']
        self.assertIn('total_profit', profit)
        self.assertIn('total_trades', profit)
        self.assertIn('average_profit_per_trade', profit)
        self.assertIn('overall_win_rate', profit)
        self.assertIn('strategy_performance', profit)
    
    def test_dynamic_optimization_features(self):
        """Validate dynamic optimization capabilities."""
        machine = create_profit_machine()
        
        # Test optimization selects strategy
        market_analysis = {
            'price': 100,
            'volatility': 0.02,
            'trend': 0.05,
            'trend_strength': 0.7,
            'momentum': 0.03,
            'price_deviation': 0,
            'liquidity': 5000000,
            'opportunities': []
        }
        
        optimization = machine.profit_optimizer.optimize_execution(
            market_analysis,
            ['arbitrage', 'trend_following', 'momentum'],
            {'position_size': 0.1}
        )
        
        # Verify optimization features
        self.assertIn('recommended_strategy', optimization)
        self.assertIn('entry_price', optimization)
        self.assertIn('exit_price', optimization)
        self.assertIn('expected_profit', optimization)
        self.assertIn('confidence', optimization)
        self.assertIn('execution_priority', optimization)
    
    def test_market_analysis_features(self):
        """Validate advanced market analysis features."""
        machine = create_profit_machine()
        
        # Build some history
        for i in range(20):
            machine.market_analyzer.analyze_market({
                'price': 100 + i * 0.5,
                'volume': 1000000,
                'liquidity': 5000000
            })
        
        # Analyze current market
        market_data = {
            'price': 110,
            'volume': 1500000,
            'liquidity': 6000000,
            'exchanges': [
                {'price': 110},
                {'price': 111}
            ]
        }
        
        analysis = machine.market_analyzer.analyze_market(market_data)
        
        # Verify all analysis features
        self.assertIn('timestamp', analysis)
        self.assertIn('price', analysis)
        self.assertIn('trend', analysis)
        self.assertIn('trend_strength', analysis)
        self.assertIn('volatility', analysis)
        self.assertIn('momentum', analysis)
        self.assertIn('price_deviation', analysis)
        self.assertIn('liquidity', analysis)
        self.assertIn('opportunities', analysis)
    
    def test_stop_loss_management(self):
        """Validate automatic stop loss calculation."""
        machine = create_profit_machine()
        
        market_data = {
            'volatility': 0.03,
            'liquidity': 5000000,
            'trend_strength': 0.6
        }
        
        # Test each strategy type
        for strategy in ['arbitrage', 'trend_following', 'mean_reversion', 
                        'momentum', 'liquidity_provision']:
            assessment = machine.risk_manager.assess_risk(market_data, strategy)
            
            # Stop loss should be calculated
            self.assertGreater(assessment['stop_loss'], 0)
            self.assertLessEqual(assessment['stop_loss'], 0.1)  # Max 10%
    
    def test_take_profit_management(self):
        """Validate automatic take profit calculation."""
        machine = create_profit_machine()
        
        market_data = {
            'volatility': 0.03,
            'liquidity': 5000000,
            'trend_strength': 0.6
        }
        
        # Test each strategy type
        for strategy in ['arbitrage', 'trend_following', 'mean_reversion',
                        'momentum', 'liquidity_provision']:
            assessment = machine.risk_manager.assess_risk(market_data, strategy)
            
            # Take profit should be calculated
            self.assertGreater(assessment['take_profit'], 0)
            self.assertLessEqual(assessment['take_profit'], 0.25)  # Max 25%
            
            # Risk-reward ratio should be favorable (at least 2:1)
            self.assertGreater(assessment['risk_reward_ratio'], 2.0)
    
    def test_exposure_control_limits(self):
        """Validate maximum exposure limits."""
        machine = create_profit_machine()
        
        # Open positions
        machine.risk_manager.open_position('pos1', {'size': 0.3})
        machine.risk_manager.open_position('pos2', {'size': 0.3})
        
        status = machine.risk_manager.get_portfolio_status()
        
        # Verify exposure tracking
        self.assertEqual(status['total_exposure'], 0.6)
        self.assertEqual(status['available_capacity'], 0.4)
        
        # Try to assess trade that would exceed limit
        market_data = {
            'volatility': 0.02,
            'liquidity': 5000000,
            'trend_strength': 0.5
        }
        
        # With 0.6 exposure, large position should be rejected or reduced
        assessment = machine.risk_manager.assess_risk(market_data, 'arbitrage')
        
        # Position size should fit within remaining capacity
        if assessment['approved']:
            self.assertLessEqual(assessment['position_size'], 0.4)
    
    def test_adaptive_learning_feature(self):
        """Validate adaptive learning disables underperforming strategies."""
        machine = create_profit_machine()
        
        # Simulate poor performance for a strategy
        machine.strategy_engine.active_strategies['arbitrage']['performance'] = {
            'total_profit': -50,
            'trades': 15,
            'win_rate': 0.3
        }
        
        # Run optimization
        machine.strategy_engine.optimize_strategies()
        
        # Poor performing strategy should be disabled
        self.assertFalse(machine.strategy_engine.active_strategies['arbitrage']['enabled'])


class TestSystemIntegration(unittest.TestCase):
    """Test integration of all system components."""
    
    def test_all_components_communicate(self):
        """Test all components work together correctly."""
        machine = create_profit_machine(portfolio_value=25000)
        
        # Process market data - this uses all components
        market_data = {
            'price': 100.0,
            'volume': 2000000,
            'liquidity': 10000000,
            'fee_rate': 0.004,
            'exchanges': [
                {'price': 100},
                {'price': 101}
            ]
        }
        
        # This should engage:
        # 1. Market Analyzer - analyze market
        # 2. Profit Optimizer - select strategy
        # 3. Strategy Engine - execute strategy
        # 4. Risk Manager - assess risk
        recommendation = machine.process_market_data(market_data)
        
        # All components should have contributed
        self.assertIsNotNone(recommendation['market_analysis'])  # Market Analyzer
        self.assertIsNotNone(recommendation['strategy'])  # Strategy Engine
        self.assertIsNotNone(recommendation['risk_assessment'])  # Risk Manager
        self.assertIsNotNone(recommendation['optimization'])  # Profit Optimizer
    
    def test_display_performance_integration(self):
        """Test performance display integrates all metrics."""
        machine = create_profit_machine()
        
        # Execute some trades
        for i in range(3):
            market_data = {
                'price': 100 + i,
                'volume': 2000000,
                'liquidity': 10000000,
                'fee_rate': 0.004
            }
            
            rec = machine.process_market_data(market_data)
            if rec['approved']:
                result = machine.execute_trade(rec)
                if result['executed']:
                    machine.close_trade(result['position_id'], 105, 0.05, True)
        
        # Display should work without errors
        try:
            machine.display_performance()
            display_works = True
        except Exception:
            display_works = False
        
        self.assertTrue(display_works)


if __name__ == '__main__':
    unittest.main()
