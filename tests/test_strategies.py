"""Tests for Advanced Production Strategies."""

import unittest
from mega_defi.strategies import (
    BaseStrategy,
    StrategyRank,
    FlashLoanArbitrageStrategy,
    CrossChainArbitrageStrategy,
    LiquidationHunterStrategy,
    MEVStrategy,
    StatisticalArbitrageStrategy,
    YieldOptimizerStrategy,
    StrategyRegistry,
)


class TestBaseStrategy(unittest.TestCase):
    """Test cases for Base Strategy."""
    
    def test_strategy_initialization(self):
        """Test that strategies initialize correctly."""
        # Flash Loan Arbitrage
        flash_loan = FlashLoanArbitrageStrategy()
        self.assertEqual(flash_loan.name, "Flash Loan Arbitrage")
        self.assertEqual(flash_loan.rank, StrategyRank.STANDARD)
        self.assertTrue(flash_loan.enabled)
        
        # Cross-Chain Arbitrage
        cross_chain = CrossChainArbitrageStrategy()
        self.assertEqual(cross_chain.name, "Cross-Chain Arbitrage")
        
        # Liquidation Hunter
        liquidation = LiquidationHunterStrategy()
        self.assertEqual(liquidation.name, "Liquidation Hunter")
        
        # MEV Strategy
        mev = MEVStrategy()
        self.assertEqual(mev.name, "MEV Strategy")
        
        # Statistical Arbitrage
        stat_arb = StatisticalArbitrageStrategy()
        self.assertEqual(stat_arb.name, "Statistical Arbitrage")
        
        # Yield Optimizer
        yield_opt = YieldOptimizerStrategy()
        self.assertEqual(yield_opt.name, "Yield Optimizer")
    
    def test_strategy_ranking_system(self):
        """Test strategy ranking calculation."""
        strategy = FlashLoanArbitrageStrategy()
        
        # Initially should be standard rank
        self.assertEqual(strategy.rank, StrategyRank.STANDARD)
        self.assertEqual(strategy.global_rank_score, 0.0)
        
        # Record some successful trades
        for _ in range(15):
            strategy.record_trade(0.05, True)  # 5% profit, successful
        
        for _ in range(5):
            strategy.record_trade(-0.01, False)  # 1% loss, unsuccessful
        
        # Check metrics updated
        self.assertEqual(strategy.total_trades, 20)
        self.assertEqual(strategy.winning_trades, 15)
        self.assertEqual(strategy.win_rate, 0.75)
        self.assertGreater(strategy.global_rank_score, 0)
        
        # Should be upgraded to higher rank
        self.assertIn(strategy.rank, [StrategyRank.PROFESSIONAL, StrategyRank.ADVANCED, StrategyRank.ELITE])
    
    def test_production_ready_criteria(self):
        """Test production ready check."""
        strategy = CrossChainArbitrageStrategy()
        
        # Not production ready initially
        self.assertFalse(strategy.is_production_ready())
        
        # Record enough successful trades
        for _ in range(12):
            strategy.record_trade(0.08, True)  # 8% profit
        
        # Should be production ready
        self.assertTrue(strategy.is_production_ready())


class TestFlashLoanArbitrageStrategy(unittest.TestCase):
    """Test cases for Flash Loan Arbitrage Strategy."""
    
    def test_analyze_finds_opportunities(self):
        """Test that strategy finds arbitrage opportunities."""
        strategy = FlashLoanArbitrageStrategy(min_profit_threshold=0.01)
        
        market_data = {
            'exchanges': [
                {'name': 'Uniswap', 'price': 100, 'liquidity': 50000},
                {'name': 'SushiSwap', 'price': 102, 'liquidity': 60000},
                {'name': 'PancakeSwap', 'price': 101, 'liquidity': 55000},
            ],
            'gas_price': 50,
        }
        
        analysis = strategy.analyze(market_data)
        
        self.assertIn('opportunities', analysis)
        self.assertGreater(len(analysis['opportunities']), 0)
        self.assertIsNotNone(analysis['best_opportunity'])
    
    def test_generate_signal(self):
        """Test signal generation."""
        strategy = FlashLoanArbitrageStrategy()
        
        market_data = {
            'exchanges': [
                {'name': 'Uniswap', 'price': 100, 'liquidity': 50000},
                {'name': 'SushiSwap', 'price': 105, 'liquidity': 60000},
            ],
            'gas_price': 50,
        }
        
        analysis = strategy.analyze(market_data)
        signal = strategy.generate_signal(analysis)
        
        self.assertIn('action', signal)
        self.assertIn('confidence', signal)
        
        if signal['action'] != 'HOLD':
            self.assertEqual(signal['action'], 'EXECUTE_ARBITRAGE')
            self.assertGreater(signal['confidence'], 0)
    
    def test_tar_score_calculation(self):
        """Test TAR (Total Arbitrage Return) score."""
        strategy = FlashLoanArbitrageStrategy()
        
        # High profit, high liquidity should give high TAR
        tar_high = strategy._calculate_tar_score(0.05, 100000, 50)
        
        # Low profit, low liquidity should give low TAR
        tar_low = strategy._calculate_tar_score(0.005, 5000, 50)
        
        self.assertGreater(tar_high, tar_low)


class TestCrossChainArbitrageStrategy(unittest.TestCase):
    """Test cases for Cross-Chain Arbitrage Strategy."""
    
    def test_analyze_cross_chain_opportunities(self):
        """Test cross-chain opportunity detection."""
        strategy = CrossChainArbitrageStrategy()
        
        market_data = {
            'chains': {
                'Ethereum': {'price': 100, 'liquidity': 100000},
                'BSC': {'price': 105, 'liquidity': 80000},
                'Polygon': {'price': 102, 'liquidity': 90000},
            }
        }
        
        analysis = strategy.analyze(market_data)
        
        self.assertIn('opportunities', analysis)
        if analysis['opportunities']:
            opp = analysis['opportunities'][0]
            self.assertIn('buy_chain', opp)
            self.assertIn('sell_chain', opp)
            self.assertIn('net_profit', opp)
    
    def test_bridge_fee_calculation(self):
        """Test bridge fee lookup."""
        strategy = CrossChainArbitrageStrategy()
        
        fee = strategy._get_bridge_fee('Ethereum', 'BSC')
        self.assertGreater(fee, 0)
        self.assertLess(fee, 0.01)  # Should be less than 1%


class TestLiquidationHunterStrategy(unittest.TestCase):
    """Test cases for Liquidation Hunter Strategy."""
    
    def test_analyze_liquidation_opportunities(self):
        """Test liquidation opportunity detection."""
        strategy = LiquidationHunterStrategy(min_health_factor=1.05)
        
        market_data = {
            'lending_positions': [
                {
                    'id': 'pos1',
                    'protocol': 'Aave',
                    'collateral_asset': 'ETH',
                    'debt_asset': 'USDC',
                    'collateral_amount': 10,
                    'debt_amount': 19000,
                    'liquidation_threshold': 0.8,
                    'liquidation_bonus': 0.05,
                    'max_liquidation_pct': 0.5,
                },
            ],
            'asset_prices': {
                'ETH': 2000,
                'USDC': 1,
            },
            'gas_price': 50,
        }
        
        analysis = strategy.analyze(market_data)
        
        self.assertIn('opportunities', analysis)
    
    def test_health_factor_calculation(self):
        """Test health factor calculation."""
        strategy = LiquidationHunterStrategy()
        
        position = {
            'collateral_asset': 'ETH',
            'debt_asset': 'USDC',
            'collateral_amount': 10,
            'debt_amount': 15000,
            'liquidation_threshold': 0.8,
        }
        
        prices = {'ETH': 2000, 'USDC': 1}
        
        health_factor = strategy._calculate_health_factor(position, prices)
        
        # Health = (10 * 2000 * 0.8) / 15000 = 16000 / 15000 = 1.067
        self.assertAlmostEqual(health_factor, 1.067, places=2)


class TestMEVStrategy(unittest.TestCase):
    """Test cases for MEV Strategy."""
    
    def test_analyze_mev_opportunities(self):
        """Test MEV opportunity detection."""
        strategy = MEVStrategy(min_transaction_size=10000)
        
        market_data = {
            'pending_transactions': [
                {
                    'hash': '0xabc123',
                    'type': 'swap',
                    'value': 50000,
                    'gas_price': 100,
                    'pool': 'pool1',
                    'token_in': 'ETH',
                    'token_out': 'USDC',
                },
            ],
            'liquidity_pools': {
                'pool1': {
                    'reserve_in': 1000000,
                    'reserve_out': 2000000000,
                },
            },
        }
        
        analysis = strategy.analyze(market_data)
        
        self.assertIn('opportunities', analysis)
    
    def test_is_mev_target(self):
        """Test MEV target identification."""
        strategy = MEVStrategy(min_transaction_size=10000)
        
        valid_tx = {
            'type': 'swap',
            'value': 50000,
            'gas_price': 100,
        }
        
        self.assertTrue(strategy._is_mev_target(valid_tx))
        
        invalid_tx = {
            'type': 'transfer',
            'value': 5000,
            'gas_price': 100,
        }
        
        self.assertFalse(strategy._is_mev_target(invalid_tx))


class TestStatisticalArbitrageStrategy(unittest.TestCase):
    """Test cases for Statistical Arbitrage Strategy."""
    
    def test_correlation_calculation(self):
        """Test correlation calculation."""
        strategy = StatisticalArbitrageStrategy()
        
        # Perfect positive correlation
        prices_a = [100, 101, 102, 103, 104]
        prices_b = [200, 202, 204, 206, 208]
        
        correlation = strategy._calculate_correlation(prices_a, prices_b)
        self.assertGreater(correlation, 0.95)
        
        # Negative correlation
        prices_c = [100, 101, 102, 103, 104]
        prices_d = [200, 198, 196, 194, 192]
        
        correlation_neg = strategy._calculate_correlation(prices_c, prices_d)
        self.assertLess(correlation_neg, -0.95)
    
    def test_z_score_calculation(self):
        """Test z-score calculation."""
        strategy = StatisticalArbitrageStrategy()
        
        # Spread with clear outlier
        spread = [0, 0, 0, 0, 0, 0, 0, 0, 0, 10]
        
        z_score = strategy._calculate_z_score(spread)
        self.assertGreater(abs(z_score), 2.0)


class TestYieldOptimizerStrategy(unittest.TestCase):
    """Test cases for Yield Optimizer Strategy."""
    
    def test_analyze_yield_opportunities(self):
        """Test yield opportunity detection."""
        strategy = YieldOptimizerStrategy(min_apy=0.10)
        
        market_data = {
            'yield_protocols': [
                {
                    'name': 'Aave',
                    'apy': 0.15,
                    'tvl': 10000000,
                    'risk_score': 0.2,
                },
                {
                    'name': 'Compound',
                    'apy': 0.12,
                    'tvl': 8000000,
                    'risk_score': 0.25,
                },
                {
                    'name': 'Risky Protocol',
                    'apy': 0.50,
                    'tvl': 100000,
                    'risk_score': 0.9,
                },
            ],
            'current_allocation': {},
        }
        
        analysis = strategy.analyze(market_data)
        
        self.assertIn('opportunities', analysis)
        self.assertGreater(len(analysis['opportunities']), 0)
    
    def test_risk_adjusted_yield(self):
        """Test risk-adjusted yield calculation."""
        strategy = YieldOptimizerStrategy()
        
        # High APY, low risk
        risk_adjusted_high = strategy._calculate_risk_adjusted_yield(0.5, 0.1, 100000000)
        
        # Same APY, high risk
        risk_adjusted_low = strategy._calculate_risk_adjusted_yield(0.5, 0.8, 100000000)
        
        self.assertGreater(risk_adjusted_high, risk_adjusted_low)


class TestStrategyRegistry(unittest.TestCase):
    """Test cases for Strategy Registry."""
    
    def test_registry_initialization(self):
        """Test registry initialization."""
        registry = StrategyRegistry()
        self.assertEqual(len(registry), 0)
    
    def test_register_strategies(self):
        """Test strategy registration."""
        registry = StrategyRegistry()
        
        flash_loan = FlashLoanArbitrageStrategy()
        cross_chain = CrossChainArbitrageStrategy()
        
        registry.register_strategy(flash_loan)
        registry.register_strategy(cross_chain)
        
        self.assertEqual(len(registry), 2)
        self.assertIsNotNone(registry.get_strategy("Flash Loan Arbitrage"))
    
    def test_global_rankings(self):
        """Test global ranking system."""
        registry = StrategyRegistry()
        
        # Register multiple strategies
        strategies = [
            FlashLoanArbitrageStrategy(),
            CrossChainArbitrageStrategy(),
            LiquidationHunterStrategy(),
        ]
        
        for strategy in strategies:
            registry.register_strategy(strategy)
        
        # Record trades for different performance levels
        strategies[0].record_trade(0.05, True)
        strategies[0].record_trade(0.04, True)
        strategies[0].record_trade(0.06, True)
        
        strategies[1].record_trade(0.03, True)
        strategies[1].record_trade(-0.01, False)
        
        # Update rankings
        registry.update_global_rankings()
        rankings = registry.get_global_rankings()
        
        self.assertEqual(len(rankings), 3)
        self.assertIn('global_position', rankings[0])
        self.assertIn('score', rankings[0])
    
    def test_get_top_strategies(self):
        """Test getting top strategies."""
        registry = StrategyRegistry()
        
        # Register and record performance
        flash_loan = FlashLoanArbitrageStrategy()
        for _ in range(10):
            flash_loan.record_trade(0.05, True)
        
        cross_chain = CrossChainArbitrageStrategy()
        for _ in range(8):
            cross_chain.record_trade(0.03, True)
        for _ in range(2):
            cross_chain.record_trade(-0.01, False)
        
        registry.register_strategy(flash_loan)
        registry.register_strategy(cross_chain)
        
        top_strategies = registry.get_top_strategies(1)
        
        self.assertEqual(len(top_strategies), 1)
        # Flash loan should be top due to better performance
        self.assertEqual(top_strategies[0].name, "Flash Loan Arbitrage")
    
    def test_get_production_ready(self):
        """Test getting production-ready strategies."""
        registry = StrategyRegistry()
        
        # Strategy 1: Production ready
        strategy1 = FlashLoanArbitrageStrategy()
        for _ in range(15):
            strategy1.record_trade(0.05, True)
        
        # Strategy 2: Not enough trades
        strategy2 = CrossChainArbitrageStrategy()
        for _ in range(5):
            strategy2.record_trade(0.03, True)
        
        registry.register_strategy(strategy1)
        registry.register_strategy(strategy2)
        
        production_ready = registry.get_production_ready_strategies()
        
        self.assertGreater(len(production_ready), 0)
        self.assertTrue(all(s.is_production_ready() for s in production_ready))
    
    def test_performance_report(self):
        """Test performance report generation."""
        registry = StrategyRegistry()
        
        flash_loan = FlashLoanArbitrageStrategy()
        flash_loan.record_trade(0.05, True)
        flash_loan.record_trade(0.03, True)
        
        registry.register_strategy(flash_loan)
        
        report = registry.get_performance_report()
        
        self.assertIn('summary', report)
        self.assertIn('global_rankings', report)
        self.assertIn('strategy_metrics', report)
        
        summary = report['summary']
        self.assertEqual(summary['total_strategies'], 1)
        self.assertEqual(summary['total_trades'], 2)


if __name__ == '__main__':
    unittest.main()
