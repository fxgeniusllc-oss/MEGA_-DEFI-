"""Social and Market Sentiment Analyzer.

This module analyzes sentiment from social media, forums, and community channels
to gauge market sentiment and predict potential movements.
"""

from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta
from collections import defaultdict
import re

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Analyzes sentiment from social media and community sources.
    
    Processes text from:
    - Twitter/X
    - Reddit
    - Telegram
    - Discord
    - Forums
    """
    
    def __init__(self):
        """Initialize the sentiment analyzer."""
        # Sentiment lexicons
        self.positive_words = {
            'bullish', 'moon', 'pump', 'gem', 'buy', 'long', 'rocket',
            'profit', 'gains', 'growth', 'winner', 'strong', 'breakout',
            'opportunity', 'accumulate', 'undervalued', 'potential'
        }
        
        self.negative_words = {
            'bearish', 'dump', 'crash', 'sell', 'short', 'scam', 'rug',
            'loss', 'drop', 'fall', 'dead', 'weak', 'overvalued', 'avoid',
            'risky', 'bubble', 'panic', 'fear'
        }
        
        # Sentiment history
        self.sentiment_history = defaultdict(list)
        self.mention_counts = defaultdict(int)
        
        # Influencer tracking
        self.influencers = {}
        
        logger.info("Sentiment Analyzer initialized")
    
    def analyze_text(self, text: str, source: str = 'unknown') -> Dict[str, Any]:
        """
        Analyze sentiment of a text post.
        
        Args:
            text: Text to analyze
            source: Source platform
            
        Returns:
            Sentiment analysis result
        """
        # Normalize text
        text_lower = text.lower()
        words = re.findall(r'\w+', text_lower)
        
        # Count sentiment words
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        
        # Calculate sentiment score
        total_sentiment_words = positive_count + negative_count
        
        if total_sentiment_words == 0:
            sentiment_score = 0.0
            sentiment = 'neutral'
        else:
            sentiment_score = (positive_count - negative_count) / total_sentiment_words
            
            if sentiment_score > 0.2:
                sentiment = 'positive'
            elif sentiment_score < -0.2:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
        
        # Detect specific tokens mentioned
        tokens_mentioned = self._extract_tokens(text)
        
        # Detect emojis/indicators
        emoji_sentiment = self._analyze_emojis(text)
        
        # Combine scores
        final_score = (sentiment_score + emoji_sentiment) / 2
        
        result = {
            'sentiment': sentiment,
            'score': final_score,
            'confidence': min(abs(final_score), 1.0),
            'positive_indicators': positive_count,
            'negative_indicators': negative_count,
            'tokens_mentioned': tokens_mentioned,
            'source': source,
            'timestamp': datetime.now().isoformat()
        }
        
        # Update mention counts
        for token in tokens_mentioned:
            self.mention_counts[token] += 1
        
        return result
    
    def analyze_token_sentiment(
        self,
        token: str,
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get aggregated sentiment for a specific token.
        
        Args:
            token: Token symbol
            time_window_hours: Time window for analysis
            
        Returns:
            Aggregated sentiment analysis
        """
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        
        # Get relevant sentiment entries
        relevant_sentiments = [
            s for s in self.sentiment_history[token]
            if datetime.fromisoformat(s['timestamp']) >= cutoff_time
        ]
        
        if not relevant_sentiments:
            return {
                'token': token,
                'sentiment': 'neutral',
                'score': 0.0,
                'confidence': 0.0,
                'sample_size': 0,
                'mention_count': self.mention_counts.get(token, 0)
            }
        
        # Calculate aggregate metrics
        avg_score = sum(s['score'] for s in relevant_sentiments) / len(relevant_sentiments)
        
        # Determine overall sentiment
        if avg_score > 0.15:
            overall_sentiment = 'positive'
        elif avg_score < -0.15:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'
        
        # Calculate sentiment distribution
        positive_count = sum(1 for s in relevant_sentiments if s['score'] > 0.2)
        negative_count = sum(1 for s in relevant_sentiments if s['score'] < -0.2)
        neutral_count = len(relevant_sentiments) - positive_count - negative_count
        
        # Calculate momentum (recent vs older sentiment)
        momentum = self._calculate_sentiment_momentum(relevant_sentiments)
        
        return {
            'token': token,
            'sentiment': overall_sentiment,
            'score': avg_score,
            'confidence': min(abs(avg_score), 1.0),
            'sample_size': len(relevant_sentiments),
            'mention_count': self.mention_counts.get(token, 0),
            'distribution': {
                'positive': positive_count,
                'neutral': neutral_count,
                'negative': negative_count
            },
            'momentum': momentum,
            'trending': self._is_trending(token)
        }
    
    def track_post(
        self,
        text: str,
        author: str,
        source: str,
        token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Track a social media post.
        
        Args:
            text: Post content
            author: Post author
            source: Platform source
            token: Optional specific token
            
        Returns:
            Analysis result
        """
        # Analyze sentiment
        analysis = self.analyze_text(text, source)
        
        # Add author information
        analysis['author'] = author
        
        # Track in history
        if token:
            tokens = [token]
        else:
            tokens = analysis['tokens_mentioned']
        
        for tok in tokens:
            self.sentiment_history[tok].append(analysis)
            
            # Keep only recent history (last 1000 posts per token)
            if len(self.sentiment_history[tok]) > 1000:
                self.sentiment_history[tok].pop(0)
        
        # Track influencer if significant
        if author not in self.influencers:
            self.influencers[author] = {
                'post_count': 0,
                'avg_sentiment': 0.0,
                'sources': set()
            }
        
        inf = self.influencers[author]
        inf['post_count'] += 1
        inf['avg_sentiment'] = (
            (inf['avg_sentiment'] * (inf['post_count'] - 1) + analysis['score']) /
            inf['post_count']
        )
        inf['sources'].add(source)
        
        logger.debug(f"Tracked post from {author} on {source}: {analysis['sentiment']}")
        
        return analysis
    
    def get_trending_tokens(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get trending tokens based on mention frequency and sentiment.
        
        Args:
            limit: Number of tokens to return
            
        Returns:
            List of trending tokens
        """
        # Calculate trending score for each token
        trending_scores = {}
        
        for token, count in self.mention_counts.items():
            sentiment_data = self.analyze_token_sentiment(token, time_window_hours=6)
            
            # Trending score = mentions * sentiment_confidence
            trending_score = count * sentiment_data['confidence']
            trending_scores[token] = {
                'token': token,
                'mentions': count,
                'sentiment': sentiment_data['sentiment'],
                'score': sentiment_data['score'],
                'trending_score': trending_score
            }
        
        # Sort by trending score
        sorted_tokens = sorted(
            trending_scores.values(),
            key=lambda x: x['trending_score'],
            reverse=True
        )
        
        return sorted_tokens[:limit]
    
    def _extract_tokens(self, text: str) -> List[str]:
        """Extract token symbols from text."""
        # Look for $SYMBOL pattern
        token_pattern = r'\$([A-Z]{2,10})\b'
        tokens = re.findall(token_pattern, text.upper())
        
        # Also look for common patterns
        common_tokens = ['BTC', 'ETH', 'USDT', 'USDC', 'BNB', 'SOL', 'ADA', 'DOT']
        for token in common_tokens:
            if token.lower() in text.lower():
                tokens.append(token)
        
        return list(set(tokens))
    
    def _analyze_emojis(self, text: str) -> float:
        """Analyze emoji sentiment."""
        positive_emojis = ['🚀', '🌙', '💎', '🔥', '💪', '📈', '🎯', '💰']
        negative_emojis = ['📉', '💩', '⚠️', '🔻', '😢', '😭']
        
        positive_count = sum(text.count(emoji) for emoji in positive_emojis)
        negative_count = sum(text.count(emoji) for emoji in negative_emojis)
        
        total = positive_count + negative_count
        if total == 0:
            return 0.0
        
        return (positive_count - negative_count) / total
    
    def _calculate_sentiment_momentum(
        self,
        sentiments: List[Dict[str, Any]]
    ) -> float:
        """Calculate sentiment momentum (recent vs historical)."""
        if len(sentiments) < 4:
            return 0.0
        
        # Split into recent and older
        split_point = len(sentiments) // 2
        older = sentiments[:split_point]
        recent = sentiments[split_point:]
        
        older_avg = sum(s['score'] for s in older) / len(older)
        recent_avg = sum(s['score'] for s in recent) / len(recent)
        
        # Momentum is the change
        return recent_avg - older_avg
    
    def _is_trending(self, token: str) -> bool:
        """Check if token is currently trending."""
        # Check recent mention frequency
        recent_mentions = sum(
            1 for s in self.sentiment_history[token]
            if datetime.fromisoformat(s['timestamp']) >= datetime.now() - timedelta(hours=1)
        )
        
        # Trending if > 5 mentions in last hour
        return recent_mentions > 5
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get sentiment analyzer statistics."""
        return {
            'tracked_tokens': len(self.sentiment_history),
            'total_posts_analyzed': sum(len(posts) for posts in self.sentiment_history.values()),
            'tracked_influencers': len(self.influencers),
            'top_mentioned_tokens': sorted(
                self.mention_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }
