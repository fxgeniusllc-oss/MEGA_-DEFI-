"""Market Analyzer - Real-time market data analysis and pattern recognition."""

from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class MarketAnalyzer:
    """
    Advanced market analysis system for DeFi markets.
    
    Analyzes price movements, liquidity, volatility, and identifies
    profitable trading opportunities.
    """
    
    def __init__(self):
        self.price_history = []
        self.volume_history = []
        self.analysis_cache = {}
        logger.info("Market Analyzer initialized")
    
    def analyze_market(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive market analysis.
        
        Args:
            market_data: Current market data including price, volume, liquidity
            
        Returns:
            Analysis results with trends, patterns, and opportunities
        """
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'price': market_data.get('price', 0),
            'volume': market_data.get('volume', 0),
            'trend': self._analyze_trend(market_data),
            'trend_strength': self._calculate_trend_strength(market_data),
            'volatility': self._calculate_volatility(market_data),
            'momentum': self._calculate_momentum(market_data),
            'price_deviation': self._calculate_price_deviation(market_data),
            'liquidity': market_data.get('liquidity', 0),
            'opportunities': self._identify_opportunities(market_data)
        }
        
        self._update_history(market_data)
        return analysis
    
    def _analyze_trend(self, market_data: Dict[str, Any]) -> float:
        """
        Analyze price trend direction.
        
        Returns:
            Positive value for uptrend, negative for downtrend
        """
        if len(self.price_history) < 2:
            return 0.0
        
        recent_prices = self.price_history[-20:] if len(self.price_history) >= 20 else self.price_history
        if len(recent_prices) < 2:
            return 0.0
        
        trend = (recent_prices[-1] - recent_prices[0]) / recent_prices[0]
        return trend
    
    def _calculate_trend_strength(self, market_data: Dict[str, Any]) -> float:
        """Calculate the strength of the current trend."""
        if len(self.price_history) < 5:
            return 0.0
        
        recent_prices = self.price_history[-10:] if len(self.price_history) >= 10 else self.price_history
        avg_price = sum(recent_prices) / len(recent_prices)
        variance = sum((p - avg_price) ** 2 for p in recent_prices) / len(recent_prices)
        
        strength = min(variance / (avg_price ** 2) * 100, 1.0) if avg_price > 0 else 0.0
        return strength
    
    def _calculate_volatility(self, market_data: Dict[str, Any]) -> float:
        """Calculate market volatility."""
        if len(self.price_history) < 2:
            return 0.0
        
        recent_prices = self.price_history[-20:] if len(self.price_history) >= 20 else self.price_history
        if len(recent_prices) < 2:
            return 0.0
        
        avg_price = sum(recent_prices) / len(recent_prices)
        variance = sum((p - avg_price) ** 2 for p in recent_prices) / len(recent_prices)
        volatility = (variance ** 0.5) / avg_price if avg_price > 0 else 0.0
        
        return volatility
    
    def _calculate_momentum(self, market_data: Dict[str, Any]) -> float:
        """Calculate price momentum."""
        if len(self.price_history) < 5:
            return 0.0
        
        recent_prices = self.price_history[-5:]
        momentum = (recent_prices[-1] - recent_prices[0]) / recent_prices[0] if recent_prices[0] > 0 else 0.0
        return momentum
    
    def _calculate_price_deviation(self, market_data: Dict[str, Any]) -> float:
        """Calculate deviation from moving average."""
        if len(self.price_history) < 10:
            return 0.0
        
        recent_prices = self.price_history[-20:] if len(self.price_history) >= 20 else self.price_history
        avg_price = sum(recent_prices) / len(recent_prices)
        current_price = market_data.get('price', avg_price)
        
        std_dev = (sum((p - avg_price) ** 2 for p in recent_prices) / len(recent_prices)) ** 0.5
        deviation = (current_price - avg_price) / std_dev if std_dev > 0 else 0.0
        
        return deviation
    
    def _identify_opportunities(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify trading opportunities based on analysis."""
        opportunities = []
        
        # Check for arbitrage opportunities
        if 'exchanges' in market_data and len(market_data['exchanges']) > 1:
            prices = [ex['price'] for ex in market_data['exchanges']]
            max_price = max(prices)
            min_price = min(prices)
            if (max_price - min_price) / min_price > 0.01:  # 1% difference
                opportunities.append({
                    'type': 'arbitrage',
                    'profit_potential': (max_price - min_price) / min_price,
                    'action': 'Buy at low exchange, sell at high exchange'
                })
        
        # Check for mean reversion opportunity
        deviation = self._calculate_price_deviation(market_data)
        if abs(deviation) > 2.0:
            opportunities.append({
                'type': 'mean_reversion',
                'profit_potential': abs(deviation) * 0.1,
                'action': 'Sell' if deviation > 0 else 'Buy'
            })
        
        # Check for momentum opportunity
        momentum = self._calculate_momentum(market_data)
        if abs(momentum) > 0.05:
            opportunities.append({
                'type': 'momentum',
                'profit_potential': abs(momentum),
                'action': 'Buy' if momentum > 0 else 'Sell'
            })
        
        return opportunities
    
    def _update_history(self, market_data: Dict[str, Any]):
        """Update price and volume history."""
        price = market_data.get('price', 0)
        volume = market_data.get('volume', 0)
        
        self.price_history.append(price)
        self.volume_history.append(volume)
        
        # Keep only last 1000 data points
        if len(self.price_history) > 1000:
            self.price_history = self.price_history[-1000:]
        if len(self.volume_history) > 1000:
            self.volume_history = self.volume_history[-1000:]
    
    def get_market_summary(self) -> Dict[str, Any]:
        """Get a summary of current market conditions."""
        if not self.price_history:
            return {'status': 'No data available'}
        
        return {
            'current_price': self.price_history[-1] if self.price_history else 0,
            'price_change_24h': self._calculate_price_change(),
            'avg_volume': sum(self.volume_history) / len(self.volume_history) if self.volume_history else 0,
            'data_points': len(self.price_history)
        }
    
    def _calculate_price_change(self) -> float:
        """Calculate 24h price change percentage."""
        if len(self.price_history) < 2:
            return 0.0
        
        # Assuming data points are collected regularly
        change = (self.price_history[-1] - self.price_history[0]) / self.price_history[0]
        return change * 100
