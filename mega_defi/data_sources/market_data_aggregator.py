"""Real-time Market Data Aggregator.

This module aggregates real-time market data from multiple DEXs
to provide comprehensive market coverage.
"""

from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class MarketDataAggregator:
    """
    Aggregates real-time market data from multiple DEXs.
    
    Collects and normalizes data from various decentralized exchanges
    to provide unified market view.
    """
    
    def __init__(self):
        """Initialize the market data aggregator."""
        self.dex_connections = {}
        self.price_feeds = defaultdict(list)
        self.liquidity_data = {}
        self.volume_data = {}
        self.last_update = {}
        
        # Supported DEXs
        self.supported_dexs = [
            'uniswap_v3',
            'sushiswap',
            'pancakeswap',
            'curve',
            'balancer',
            'dodo',
            '1inch',
            'kyberswap'
        ]
        
        logger.info("Market Data Aggregator initialized")
    
    def register_dex(self, dex_name: str, connection_params: Dict[str, Any]) -> None:
        """
        Register a DEX connection for data aggregation.
        
        Args:
            dex_name: Name of the DEX
            connection_params: Connection parameters (RPC, API keys, etc.)
        """
        if dex_name not in self.supported_dexs:
            logger.warning(f"DEX {dex_name} not in supported list")
        
        self.dex_connections[dex_name] = connection_params
        logger.info(f"Registered DEX: {dex_name}")
    
    def get_aggregated_price(
        self,
        token_pair: str,
        method: str = 'volume_weighted'
    ) -> Dict[str, Any]:
        """
        Get aggregated price across all DEXs.
        
        Args:
            token_pair: Trading pair (e.g., 'ETH/USDC')
            method: Aggregation method ('volume_weighted', 'median', 'mean')
            
        Returns:
            Aggregated price data
        """
        prices = self.price_feeds.get(token_pair, [])
        
        if not prices:
            return {
                'price': 0.0,
                'confidence': 0.0,
                'source_count': 0,
                'timestamp': datetime.now().isoformat()
            }
        
        if method == 'volume_weighted':
            aggregated_price = self._volume_weighted_price(prices)
        elif method == 'median':
            aggregated_price = self._median_price(prices)
        else:
            aggregated_price = self._mean_price(prices)
        
        return {
            'price': aggregated_price,
            'confidence': self._calculate_confidence(prices),
            'source_count': len(prices),
            'spread': self._calculate_spread(prices),
            'timestamp': datetime.now().isoformat(),
            'sources': [p['dex'] for p in prices]
        }
    
    def get_liquidity_depth(
        self,
        token_pair: str,
        depth_levels: int = 10
    ) -> Dict[str, Any]:
        """
        Get aggregated liquidity depth across DEXs.
        
        Args:
            token_pair: Trading pair
            depth_levels: Number of price levels to aggregate
            
        Returns:
            Aggregated liquidity depth
        """
        liquidity = self.liquidity_data.get(token_pair, {})
        
        total_bid_liquidity = sum(
            liq.get('bid_liquidity', 0)
            for liq in liquidity.values()
        )
        
        total_ask_liquidity = sum(
            liq.get('ask_liquidity', 0)
            for liq in liquidity.values()
        )
        
        return {
            'token_pair': token_pair,
            'bid_liquidity': total_bid_liquidity,
            'ask_liquidity': total_ask_liquidity,
            'total_liquidity': total_bid_liquidity + total_ask_liquidity,
            'dex_count': len(liquidity),
            'imbalance': self._calculate_imbalance(total_bid_liquidity, total_ask_liquidity)
        }
    
    def get_volume_24h(self, token_pair: str) -> Dict[str, Any]:
        """
        Get aggregated 24-hour volume.
        
        Args:
            token_pair: Trading pair
            
        Returns:
            Volume statistics
        """
        volumes = self.volume_data.get(token_pair, {})
        
        total_volume = sum(vol.get('volume_24h', 0) for vol in volumes.values())
        
        return {
            'token_pair': token_pair,
            'volume_24h': total_volume,
            'dex_breakdown': {
                dex: vol.get('volume_24h', 0)
                for dex, vol in volumes.items()
            },
            'most_liquid_dex': max(
                volumes.items(),
                key=lambda x: x[1].get('volume_24h', 0)
            )[0] if volumes else None
        }
    
    def update_market_data(
        self,
        token_pair: str,
        dex_name: str,
        price: float,
        volume: float,
        liquidity: Dict[str, float]
    ) -> None:
        """
        Update market data from a DEX.
        
        Args:
            token_pair: Trading pair
            dex_name: DEX name
            price: Current price
            volume: Trading volume
            liquidity: Liquidity data
        """
        # Update price feed
        price_data = {
            'dex': dex_name,
            'price': price,
            'volume': volume,
            'timestamp': datetime.now().isoformat()
        }
        
        # Keep only recent prices (last 100)
        self.price_feeds[token_pair].append(price_data)
        if len(self.price_feeds[token_pair]) > 100:
            self.price_feeds[token_pair].pop(0)
        
        # Update volume data
        if token_pair not in self.volume_data:
            self.volume_data[token_pair] = {}
        self.volume_data[token_pair][dex_name] = {'volume_24h': volume}
        
        # Update liquidity data
        if token_pair not in self.liquidity_data:
            self.liquidity_data[token_pair] = {}
        self.liquidity_data[token_pair][dex_name] = liquidity
        
        # Update timestamp
        self.last_update[token_pair] = datetime.now()
    
    def identify_arbitrage_opportunities(
        self,
        token_pair: str,
        min_profit_threshold: float = 0.005
    ) -> List[Dict[str, Any]]:
        """
        Identify arbitrage opportunities across DEXs.
        
        Args:
            token_pair: Trading pair
            min_profit_threshold: Minimum profit percentage
            
        Returns:
            List of arbitrage opportunities
        """
        prices = self.price_feeds.get(token_pair, [])
        
        if len(prices) < 2:
            return []
        
        opportunities = []
        
        # Compare all pairs of DEXs
        for i, price1 in enumerate(prices):
            for price2 in prices[i+1:]:
                profit_pct = abs(price1['price'] - price2['price']) / min(price1['price'], price2['price'])
                
                if profit_pct >= min_profit_threshold:
                    if price1['price'] < price2['price']:
                        buy_dex, sell_dex = price1['dex'], price2['dex']
                        buy_price, sell_price = price1['price'], price2['price']
                    else:
                        buy_dex, sell_dex = price2['dex'], price1['dex']
                        buy_price, sell_price = price2['price'], price1['price']
                    
                    opportunities.append({
                        'token_pair': token_pair,
                        'buy_dex': buy_dex,
                        'sell_dex': sell_dex,
                        'buy_price': buy_price,
                        'sell_price': sell_price,
                        'profit_percentage': profit_pct,
                        'estimated_profit': (sell_price - buy_price) / buy_price
                    })
        
        # Sort by profit
        opportunities.sort(key=lambda x: x['profit_percentage'], reverse=True)
        
        return opportunities
    
    def _volume_weighted_price(self, prices: List[Dict[str, Any]]) -> float:
        """Calculate volume-weighted average price."""
        total_volume = sum(p.get('volume', 1) for p in prices)
        
        if total_volume == 0:
            return self._mean_price(prices)
        
        weighted_sum = sum(p['price'] * p.get('volume', 1) for p in prices)
        return weighted_sum / total_volume
    
    def _median_price(self, prices: List[Dict[str, Any]]) -> float:
        """Calculate median price."""
        sorted_prices = sorted(p['price'] for p in prices)
        n = len(sorted_prices)
        
        if n % 2 == 0:
            return (sorted_prices[n//2 - 1] + sorted_prices[n//2]) / 2
        else:
            return sorted_prices[n//2]
    
    def _mean_price(self, prices: List[Dict[str, Any]]) -> float:
        """Calculate mean price."""
        return sum(p['price'] for p in prices) / len(prices)
    
    def _calculate_confidence(self, prices: List[Dict[str, Any]]) -> float:
        """Calculate confidence based on price consistency."""
        if len(prices) < 2:
            return 0.5
        
        avg_price = self._mean_price(prices)
        variance = sum((p['price'] - avg_price) ** 2 for p in prices) / len(prices)
        std_dev = variance ** 0.5
        
        # Coefficient of variation (lower is better)
        cv = std_dev / avg_price if avg_price > 0 else 1.0
        
        # Convert to confidence (0-1)
        confidence = max(0.0, min(1.0, 1.0 - cv))
        return confidence
    
    def _calculate_spread(self, prices: List[Dict[str, Any]]) -> float:
        """Calculate price spread across DEXs."""
        if not prices:
            return 0.0
        
        price_values = [p['price'] for p in prices]
        return (max(price_values) - min(price_values)) / min(price_values)
    
    def _calculate_imbalance(self, bid: float, ask: float) -> float:
        """Calculate liquidity imbalance."""
        total = bid + ask
        if total == 0:
            return 0.0
        return (bid - ask) / total
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get aggregator statistics."""
        return {
            'connected_dexs': len(self.dex_connections),
            'tracked_pairs': len(self.price_feeds),
            'total_price_points': sum(len(prices) for prices in self.price_feeds.values()),
            'supported_dexs': self.supported_dexs.copy()
        }
