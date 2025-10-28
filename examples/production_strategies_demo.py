#!/usr/bin/env python3
"""
MEGA DeFi - Production Strategy Demo
=====================================

Demonstrates the advanced production-ready strategies with global ranking system.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mega_defi.strategies import (
    FlashLoanArbitrageStrategy,
    CrossChainArbitrageStrategy,
    LiquidationHunterStrategy,
    MEVStrategy,
    StatisticalArbitrageStrategy,
    YieldOptimizerStrategy,
    StrategyRegistry,
)


def demonstrate_flash_loan_arbitrage():
    """Demonstrate Flash Loan Arbitrage Strategy."""
    print("\n" + "=" * 70)
    print("1. FLASH LOAN ARBITRAGE STRATEGY")
    print("=" * 70)
    
    strategy = FlashLoanArbitrageStrategy(
        min_profit_threshold=0.005,
        max_gas_cost=500,
        min_liquidity=10000
    )
    
    # Simulated market data with price differences
    market_data = {
        'exchanges': [
            {'name': 'Uniswap', 'price': 2000, 'liquidity': 100000},
            {'name': 'SushiSwap', 'price': 2050, 'liquidity': 120000},
            {'name': 'PancakeSwap', 'price': 2025, 'liquidity': 90000},
        ],
        'gas_price': 50,
    }
    
    # Analyze opportunities
    analysis = strategy.analyze(market_data)
    print(f"\n✓ Found {analysis['total_opportunities']} arbitrage opportunities")
    
    if analysis['best_opportunity']:
        opp = analysis['best_opportunity']
        print(f"\n📊 Best Opportunity:")
        print(f"   Buy on: {opp['buy_exchange']} @ ${opp['buy_price']:.2f}")
        print(f"   Sell on: {opp['sell_exchange']} @ ${opp['sell_price']:.2f}")
        print(f"   Profit: {opp['profit_percentage']*100:.2f}%")
        print(f"   TAR Score: {opp['tar_score']:.2f}")
        print(f"   Liquidity: ${opp['available_liquidity']:,.0f}")
    
    # Generate signal
    signal = strategy.generate_signal(analysis)
    print(f"\n🎯 Signal: {signal['action']}")
    print(f"   Confidence: {signal['confidence']*100:.1f}%")
    
    # Record some trades for ranking
    for _ in range(15):
        strategy.record_trade(0.05, True)
    for _ in range(3):
        strategy.record_trade(-0.01, False)
    
    print(f"\n📈 Strategy Performance:")
    print(f"   Global Rank: {strategy.rank.value}")
    print(f"   Rank Score: {strategy.global_rank_score:.2f}")
    print(f"   Win Rate: {strategy.win_rate*100:.1f}%")
    print(f"   Production Ready: {'✓ YES' if strategy.is_production_ready() else '✗ NO'}")
    
    return strategy


def demonstrate_cross_chain_arbitrage():
    """Demonstrate Cross-Chain Arbitrage Strategy."""
    print("\n" + "=" * 70)
    print("2. CROSS-CHAIN ARBITRAGE STRATEGY")
    print("=" * 70)
    
    strategy = CrossChainArbitrageStrategy(
        min_profit_after_fees=0.03,
        max_bridge_time=600
    )
    
    market_data = {
        'chains': {
            'Ethereum': {'price': 2000, 'liquidity': 500000},
            'BSC': {'price': 2080, 'liquidity': 400000},
            'Polygon': {'price': 2040, 'liquidity': 350000},
            'Arbitrum': {'price': 2010, 'liquidity': 300000},
        }
    }
    
    analysis = strategy.analyze(market_data)
    print(f"\n✓ Found {analysis['total_opportunities']} cross-chain opportunities")
    
    if analysis['best_opportunity']:
        opp = analysis['best_opportunity']
        print(f"\n📊 Best Opportunity:")
        print(f"   Buy on: {opp['buy_chain']} @ ${opp['buy_price']:.2f}")
        print(f"   Sell on: {opp['sell_chain']} @ ${opp['sell_price']:.2f}")
        print(f"   Net Profit: {opp['net_profit']*100:.2f}%")
        print(f"   Bridge Time: {opp['bridge_time']}s")
        print(f"   Bridge Fee: {opp['bridge_fee']*100:.3f}%")
    
    # Record trades
    for _ in range(12):
        strategy.record_trade(0.04, True)
    for _ in range(2):
        strategy.record_trade(-0.01, False)
    
    print(f"\n📈 Strategy Performance:")
    print(f"   Global Rank: {strategy.rank.value}")
    print(f"   Rank Score: {strategy.global_rank_score:.2f}")
    print(f"   Production Ready: {'✓ YES' if strategy.is_production_ready() else '✗ NO'}")
    
    return strategy


def demonstrate_liquidation_hunter():
    """Demonstrate Liquidation Hunter Strategy."""
    print("\n" + "=" * 70)
    print("3. LIQUIDATION HUNTER STRATEGY")
    print("=" * 70)
    
    strategy = LiquidationHunterStrategy(
        min_health_factor=1.05,
        min_liquidation_profit=0.02
    )
    
    market_data = {
        'lending_positions': [
            {
                'id': 'pos1',
                'protocol': 'Aave',
                'collateral_asset': 'ETH',
                'debt_asset': 'USDC',
                'collateral_amount': 100,
                'debt_amount': 190000,
                'liquidation_threshold': 0.8,
                'liquidation_bonus': 0.05,
                'max_liquidation_pct': 0.5,
            },
            {
                'id': 'pos2',
                'protocol': 'Compound',
                'collateral_asset': 'BTC',
                'debt_asset': 'USDC',
                'collateral_amount': 5,
                'debt_amount': 245000,
                'liquidation_threshold': 0.75,
                'liquidation_bonus': 0.08,
                'max_liquidation_pct': 0.5,
            },
        ],
        'asset_prices': {
            'ETH': 2000,
            'BTC': 50000,
            'USDC': 1,
        },
        'gas_price': 50,
    }
    
    analysis = strategy.analyze(market_data)
    print(f"\n✓ Monitoring {strategy.positions_monitored} positions")
    print(f"✓ Found {analysis['total_opportunities']} liquidation opportunities")
    
    if analysis['best_opportunity']:
        opp = analysis['best_opportunity']
        print(f"\n📊 Best Liquidation:")
        print(f"   Protocol: {opp['protocol']}")
        print(f"   Health Factor: {opp['health_factor']:.4f}")
        print(f"   Expected Profit: {opp['liquidation_profit']*100:.2f}%")
        print(f"   Urgency Score: {opp['urgency_score']:.1f}/10")
    
    # Record trades
    for _ in range(10):
        strategy.record_trade(0.08, True)
    
    print(f"\n📈 Strategy Performance:")
    print(f"   Global Rank: {strategy.rank.value}")
    print(f"   Rank Score: {strategy.global_rank_score:.2f}")
    print(f"   Production Ready: {'✓ YES' if strategy.is_production_ready() else '✗ NO'}")
    
    return strategy


def demonstrate_mev_strategy():
    """Demonstrate MEV Strategy."""
    print("\n" + "=" * 70)
    print("4. MEV STRATEGY (Sandwich Attacks)")
    print("=" * 70)
    
    strategy = MEVStrategy(
        min_transaction_size=10000,
        min_expected_profit=0.01
    )
    
    market_data = {
        'pending_transactions': [
            {
                'hash': '0xabc123',
                'type': 'swap',
                'value': 50000,
                'gas_price': 100,
                'pool': 'ETH-USDC',
                'token_in': 'ETH',
                'token_out': 'USDC',
            },
            {
                'hash': '0xdef456',
                'type': 'swap',
                'value': 100000,
                'gas_price': 80,
                'pool': 'WBTC-USDC',
                'token_in': 'WBTC',
                'token_out': 'USDC',
            },
        ],
        'liquidity_pools': {
            'ETH-USDC': {
                'reserve_in': 5000000,
                'reserve_out': 10000000000,
            },
            'WBTC-USDC': {
                'reserve_in': 2000000,
                'reserve_out': 100000000000,
            },
        },
    }
    
    analysis = strategy.analyze(market_data)
    print(f"\n✓ Detected {strategy.mev_opportunities_detected} MEV opportunities")
    
    if analysis['best_opportunity']:
        opp = analysis['best_opportunity']
        print(f"\n📊 Best MEV Opportunity:")
        print(f"   Type: {opp['type']}")
        print(f"   Target Size: ${opp['target_size']:,.0f}")
        print(f"   Expected Profit: {opp['expected_profit']*100:.2f}%")
        print(f"   MEV Score: {opp['mev_score']:.2f}")
    
    # Record trades
    for _ in range(20):
        strategy.record_trade(0.06, True)
    for _ in range(2):
        strategy.record_trade(-0.005, False)
    
    print(f"\n📈 Strategy Performance:")
    print(f"   Global Rank: {strategy.rank.value}")
    print(f"   Rank Score: {strategy.global_rank_score:.2f}")
    print(f"   Production Ready: {'✓ YES' if strategy.is_production_ready() else '✗ NO'}")
    
    return strategy


def demonstrate_stat_arb():
    """Demonstrate Statistical Arbitrage Strategy."""
    print("\n" + "=" * 70)
    print("5. STATISTICAL ARBITRAGE STRATEGY")
    print("=" * 70)
    
    strategy = StatisticalArbitrageStrategy(
        z_score_threshold=2.0,
        correlation_threshold=0.7
    )
    
    # Simulated price history showing mean reversion
    market_data = {
        'asset_pairs': [
            {'asset_a': 'ETH', 'asset_b': 'BTC'},
        ],
        'price_history': {
            'ETH': [2000, 2010, 2020, 2030, 2040, 2050, 2060, 2070, 2080, 2100, 
                    2110, 2120, 2130, 2140, 2150, 2160, 2170, 2180, 2190, 2200,
                    2210, 2220, 2230, 2240, 2250, 2260, 2270, 2280, 2290, 2400],
            'BTC': [50000, 50200, 50400, 50600, 50800, 51000, 51200, 51400, 51600, 51800,
                    52000, 52200, 52400, 52600, 52800, 53000, 53200, 53400, 53600, 53800,
                    54000, 54200, 54400, 54600, 54800, 55000, 55200, 55400, 55600, 58000],
        },
    }
    
    analysis = strategy.analyze(market_data)
    print(f"\n✓ Analyzed {strategy.pairs_analyzed} asset pairs")
    print(f"✓ Found {analysis['total_opportunities']} statistical arbitrage opportunities")
    
    if analysis['best_opportunity']:
        opp = analysis['best_opportunity']
        print(f"\n📊 Best Stat Arb Opportunity:")
        print(f"   Pair: {opp['asset_a']} / {opp['asset_b']}")
        print(f"   Correlation: {opp['correlation']:.4f}")
        print(f"   Z-Score: {opp['z_score']:.2f}")
        print(f"   Signal: {opp['signal']}")
    
    # Record trades
    for _ in range(14):
        strategy.record_trade(0.03, True)
    for _ in range(3):
        strategy.record_trade(-0.01, False)
    
    print(f"\n📈 Strategy Performance:")
    print(f"   Global Rank: {strategy.rank.value}")
    print(f"   Rank Score: {strategy.global_rank_score:.2f}")
    print(f"   Production Ready: {'✓ YES' if strategy.is_production_ready() else '✗ NO'}")
    
    return strategy


def demonstrate_yield_optimizer():
    """Demonstrate Yield Optimizer Strategy."""
    print("\n" + "=" * 70)
    print("6. YIELD OPTIMIZER STRATEGY")
    print("=" * 70)
    
    strategy = YieldOptimizerStrategy(
        min_apy=0.15,
        max_protocol_risk=0.5
    )
    
    market_data = {
        'yield_protocols': [
            {'name': 'Aave', 'apy': 0.18, 'tvl': 15000000, 'risk_score': 0.2},
            {'name': 'Compound', 'apy': 0.15, 'tvl': 12000000, 'risk_score': 0.25},
            {'name': 'Curve', 'apy': 0.35, 'tvl': 8000000, 'risk_score': 0.3},
            {'name': 'Yearn', 'apy': 0.42, 'tvl': 6000000, 'risk_score': 0.35},
            {'name': 'Convex', 'apy': 0.28, 'tvl': 10000000, 'risk_score': 0.28},
        ],
        'current_allocation': {},
    }
    
    analysis = strategy.analyze(market_data)
    print(f"\n✓ Monitoring {strategy.protocols_monitored} yield protocols")
    print(f"✓ Found {analysis['total_opportunities']} yield opportunities")
    
    if analysis['best_opportunity']:
        opp = analysis['best_opportunity']
        print(f"\n📊 Best Yield Opportunity:")
        print(f"   Protocol: {opp['protocol']}")
        print(f"   APY: {opp['apy']*100:.2f}%")
        print(f"   Risk-Adjusted APY: {opp['risk_adjusted_apy']*100:.2f}%")
        print(f"   TVL: ${opp['tvl']:,.0f}")
        print(f"   Risk Score: {opp['risk_score']:.2f}")
    
    # Record trades
    for _ in range(11):
        strategy.record_trade(0.025, True)
    
    print(f"\n📈 Strategy Performance:")
    print(f"   Global Rank: {strategy.rank.value}")
    print(f"   Rank Score: {strategy.global_rank_score:.2f}")
    print(f"   Production Ready: {'✓ YES' if strategy.is_production_ready() else '✗ NO'}")
    
    return strategy


def demonstrate_global_rankings():
    """Demonstrate Global Strategy Rankings."""
    print("\n" + "=" * 70)
    print("GLOBAL STRATEGY RANKINGS & REGISTRY")
    print("=" * 70)
    
    # Create registry
    registry = StrategyRegistry()
    
    # Register all strategies
    print("\n📝 Registering all production strategies...")
    strategies = [
        demonstrate_flash_loan_arbitrage(),
        demonstrate_cross_chain_arbitrage(),
        demonstrate_liquidation_hunter(),
        demonstrate_mev_strategy(),
        demonstrate_stat_arb(),
        demonstrate_yield_optimizer(),
    ]
    
    for strategy in strategies:
        registry.register_strategy(strategy)
    
    # Display rankings
    registry.display_rankings()
    
    # Show top strategies
    print("\n🏆 TOP 3 STRATEGIES:")
    top_strategies = registry.get_top_strategies(3)
    for i, strategy in enumerate(top_strategies, 1):
        metrics = strategy.get_performance_metrics()
        print(f"\n   {i}. {metrics['name']}")
        print(f"      Rank: {metrics['rank']}")
        print(f"      Score: {metrics['global_rank_score']:.2f}")
        print(f"      Win Rate: {metrics['win_rate']*100:.1f}%")
        print(f"      Profit Factor: {metrics['profit_factor']:.2f}")
    
    # Show elite strategies
    elite = registry.get_elite_strategies()
    print(f"\n⭐ ELITE STRATEGIES: {len(elite)}")
    for strategy in elite:
        print(f"   • {strategy.name} (Score: {strategy.global_rank_score:.2f})")
    
    # Show production ready
    production_ready = registry.get_production_ready_strategies()
    print(f"\n✅ PRODUCTION READY: {len(production_ready)} strategies")
    
    # Performance report
    report = registry.get_performance_report()
    summary = report['summary']
    
    print(f"\n📊 AGGREGATE PERFORMANCE:")
    print(f"   Total Strategies: {summary['total_strategies']}")
    print(f"   Production Ready: {summary['production_ready']}")
    print(f"   Elite Tier: {summary['elite_strategies']}")
    print(f"   Total Trades: {summary['total_trades']}")
    print(f"   Net Profit: ${summary['net_profit']:.2f}")
    print(f"   Overall Win Rate: {summary['overall_win_rate']*100:.1f}%")


def main():
    """Run complete production strategy demonstration."""
    print("\n" + "="*70)
    print("🚀 MEGA DEFI - PRODUCTION STRATEGY DEMONSTRATION")
    print("="*70)
    print("\nDemonstrating 6 Elite Production Strategies:")
    print("1. Flash Loan Arbitrage (TAR Scoring)")
    print("2. Cross-Chain Arbitrage (Multi-Chain)")
    print("3. Liquidation Hunter (Lending Protocols)")
    print("4. MEV Strategy (Sandwich Attacks)")
    print("5. Statistical Arbitrage (Mean Reversion)")
    print("6. Yield Optimizer (Dynamic Allocation)")
    print("\n" + "="*70)
    
    # Demonstrate all strategies and global rankings
    demonstrate_global_rankings()
    
    print("\n" + "="*70)
    print("✅ DEMONSTRATION COMPLETE")
    print("="*70)
    print("\n💡 KEY FEATURES:")
    print("   • Global ranking system for strategy selection")
    print("   • Production-ready validation")
    print("   • Elite tier identification")
    print("   • Comprehensive performance tracking")
    print("   • Real-time strategy optimization")
    print("\n🎯 Ready for live production operations!")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
