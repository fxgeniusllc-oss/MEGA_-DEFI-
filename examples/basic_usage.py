#!/usr/bin/env python3
"""
MEGA DeFi Profit Machine - Example Usage
========================================

This example demonstrates how to use the Profit Machine with simulated market data.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import random
from mega_defi.profit_machine import create_profit_machine


def generate_market_data(base_price=100, volatility=0.02):
    """Generate simulated market data."""
    price_change = random.gauss(0, volatility)
    price = base_price * (1 + price_change)
    
    return {
        'price': price,
        'volume': random.uniform(100000, 1000000),
        'liquidity': random.uniform(500000, 5000000),
        'fee_rate': random.uniform(0.001, 0.005),
        'exchanges': [
            {'name': 'Exchange A', 'price': price * random.uniform(0.99, 1.01)},
            {'name': 'Exchange B', 'price': price * random.uniform(0.99, 1.01)},
            {'name': 'Exchange C', 'price': price * random.uniform(0.99, 1.01)},
        ]
    }


def main():
    """Run the Profit Machine example."""
    print("🚀 Starting MEGA DeFi Profit Machine Demo")
    print("=" * 60)
    
    # Create profit machine with $10,000 portfolio
    machine = create_profit_machine(
        portfolio_value=10000,
        max_risk_per_trade=0.02,  # 2% risk per trade
        max_position_size=0.1      # 10% max position size
    )
    
    # Simulate trading for multiple iterations
    base_price = 100
    num_iterations = 20
    
    print(f"\n📊 Running {num_iterations} market cycles...\n")
    
    active_trades = {}
    
    for i in range(num_iterations):
        print(f"--- Cycle {i+1}/{num_iterations} ---")
        
        # Generate market data
        market_data = generate_market_data(base_price, volatility=0.02)
        base_price = market_data['price']
        
        print(f"Market Price: ${market_data['price']:.2f}")
        
        # Process market data
        recommendation = machine.process_market_data(market_data)
        
        # Execute trade if approved
        if recommendation['approved']:
            result = machine.execute_trade(recommendation)
            if result['executed']:
                active_trades[result['position_id']] = {
                    'entry_price': result['entry_price'],
                    'stop_loss': result['stop_loss'],
                    'take_profit': result['take_profit'],
                    'cycle': i
                }
        
        # Check and close active trades
        trades_to_close = []
        for position_id, trade in active_trades.items():
            current_price = market_data['price']
            entry_price = trade['entry_price']
            
            # Calculate profit/loss percentage
            price_change = (current_price - entry_price) / entry_price
            
            # Check if stop loss or take profit hit
            if abs(price_change) >= trade['stop_loss'] or abs(price_change) >= trade['take_profit']:
                profit = price_change
                success = abs(price_change) >= trade['take_profit'] * 0.5
                
                machine.close_trade(position_id, current_price, profit, success)
                trades_to_close.append(position_id)
        
        # Remove closed trades
        for position_id in trades_to_close:
            del active_trades[position_id]
        
        print()
        time.sleep(0.1)  # Small pause for readability
    
    # Close any remaining trades
    for position_id, trade in active_trades.items():
        machine.close_trade(position_id, base_price, 0.01, True)
    
    # Display final performance report
    machine.display_performance()
    
    print("✅ Demo completed successfully!")
    print("\n💡 The Profit Machine demonstrates:")
    print("   • Strategic market analysis")
    print("   • Multi-strategy execution")
    print("   • Advanced risk management")
    print("   • Dynamic profit optimization")
    print("\n🎯 Vision + Technical Expertise = UNSTOPPABLE PROFIT MACHINE")


if __name__ == "__main__":
    main()
