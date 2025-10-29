"""Data Sources for MEGA DeFi Profit Machine.

This module provides advanced data integration capabilities including:
- Real-time market data from all DEXs
- Whale tracker integration
- Social sentiment analysis
- News sentiment processing
- On-chain analytics
"""

from .market_data_aggregator import MarketDataAggregator
from .whale_tracker import WhaleTracker
from .sentiment_analyzer import SentimentAnalyzer
from .news_processor import NewsProcessor
from .onchain_analytics import OnChainAnalytics

__all__ = [
    'MarketDataAggregator',
    'WhaleTracker',
    'SentimentAnalyzer',
    'NewsProcessor',
    'OnChainAnalytics',
]
