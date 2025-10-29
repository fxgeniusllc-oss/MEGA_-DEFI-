"""News Sentiment Processor.

This module processes and analyzes news articles and announcements
to extract market-moving information and sentiment.
"""

from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta
from collections import defaultdict
import re

logger = logging.getLogger(__name__)


class NewsProcessor:
    """
    Processes news articles and announcements for market intelligence.
    
    Analyzes news from:
    - Crypto news sites
    - Project announcements
    - Regulatory updates
    - Partnership news
    - Exchange listings
    """
    
    def __init__(self):
        """Initialize the news processor."""
        # News categories and their impact weights
        self.news_categories = {
            'listing': {'weight': 0.8, 'impact': 'positive'},
            'partnership': {'weight': 0.7, 'impact': 'positive'},
            'upgrade': {'weight': 0.6, 'impact': 'positive'},
            'hack': {'weight': 0.9, 'impact': 'negative'},
            'regulation': {'weight': 0.7, 'impact': 'negative'},
            'delisting': {'weight': 0.8, 'impact': 'negative'},
            'audit': {'weight': 0.5, 'impact': 'positive'}
        }
        
        # Keywords for categorization
        self.category_keywords = {
            'listing': ['list', 'listing', 'exchange', 'launch', 'debut'],
            'partnership': ['partner', 'partnership', 'collaborate', 'alliance'],
            'upgrade': ['upgrade', 'update', 'improvement', 'v2', 'v3'],
            'hack': ['hack', 'exploit', 'breach', 'attack', 'vulnerability'],
            'regulation': ['regulation', 'sec', 'ban', 'legal', 'compliance'],
            'delisting': ['delist', 'delisting', 'remove', 'suspend'],
            'audit': ['audit', 'security', 'certik', 'review']
        }
        
        # News storage
        self.news_articles = []
        self.token_news = defaultdict(list)
        self.news_impact_scores = {}
        
        logger.info("News Processor initialized")
    
    def process_article(
        self,
        title: str,
        content: str,
        source: str,
        tokens: Optional[List[str]] = None,
        publish_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Process a news article.
        
        Args:
            title: Article title
            content: Article content
            source: News source
            tokens: Related tokens
            publish_time: Publication timestamp
            
        Returns:
            Processed article with sentiment and impact
        """
        if publish_time is None:
            publish_time = datetime.now()
        
        # Extract tokens if not provided
        if tokens is None:
            tokens = self._extract_tokens_from_text(title + ' ' + content)
        
        # Categorize the news
        category = self._categorize_news(title + ' ' + content)
        
        # Calculate sentiment and impact
        sentiment = self._calculate_news_sentiment(title, content, category)
        impact_score = self._calculate_impact_score(category, source, sentiment)
        
        article = {
            'title': title,
            'content': content,
            'source': source,
            'tokens': tokens,
            'category': category,
            'sentiment': sentiment,
            'impact_score': impact_score,
            'publish_time': publish_time,
            'processed_time': datetime.now()
        }
        
        # Store article
        self.news_articles.append(article)
        for token in tokens:
            self.token_news[token].append(article)
        
        logger.info(
            f"Processed news: {category} - {sentiment['sentiment']} "
            f"(impact: {impact_score:.2f}) for {tokens}"
        )
        
        return article
    
    def get_token_news_sentiment(
        self,
        token: str,
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get aggregated news sentiment for a token.
        
        Args:
            token: Token symbol
            time_window_hours: Time window for analysis
            
        Returns:
            News sentiment analysis
        """
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        
        # Get recent news for token
        recent_news = [
            article for article in self.token_news[token]
            if article['publish_time'] >= cutoff_time
        ]
        
        if not recent_news:
            return {
                'token': token,
                'sentiment': 'neutral',
                'impact_score': 0.0,
                'news_count': 0,
                'categories': {}
            }
        
        # Aggregate sentiment
        total_impact = sum(article['impact_score'] for article in recent_news)
        weighted_sentiment = sum(
            article['sentiment']['score'] * article['impact_score']
            for article in recent_news
        )
        
        avg_sentiment_score = weighted_sentiment / total_impact if total_impact > 0 else 0.0
        
        # Determine overall sentiment
        if avg_sentiment_score > 0.2:
            overall_sentiment = 'positive'
        elif avg_sentiment_score < -0.2:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'
        
        # Count by category
        category_counts = defaultdict(int)
        for article in recent_news:
            category_counts[article['category']] += 1
        
        return {
            'token': token,
            'sentiment': overall_sentiment,
            'sentiment_score': avg_sentiment_score,
            'impact_score': total_impact / len(recent_news),
            'news_count': len(recent_news),
            'categories': dict(category_counts),
            'latest_news': recent_news[-3:]  # Last 3 articles
        }
    
    def detect_market_events(
        self,
        time_window_hours: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Detect significant market-moving events.
        
        Args:
            time_window_hours: Time window to check
            
        Returns:
            List of significant events
        """
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        
        # Get recent high-impact news
        significant_events = []
        
        for article in self.news_articles:
            if article['publish_time'] < cutoff_time:
                continue
            
            # Filter for high impact
            if article['impact_score'] >= 0.7:
                event = {
                    'type': 'news_event',
                    'category': article['category'],
                    'title': article['title'],
                    'tokens': article['tokens'],
                    'sentiment': article['sentiment']['sentiment'],
                    'impact_score': article['impact_score'],
                    'time': article['publish_time'].isoformat(),
                    'urgency': self._calculate_urgency(article)
                }
                significant_events.append(event)
        
        # Sort by impact
        significant_events.sort(key=lambda x: x['impact_score'], reverse=True)
        
        return significant_events
    
    def get_breaking_news(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get most recent breaking news.
        
        Args:
            limit: Number of articles to return
            
        Returns:
            Recent news articles
        """
        # Sort by publish time
        sorted_news = sorted(
            self.news_articles,
            key=lambda x: x['publish_time'],
            reverse=True
        )
        
        return sorted_news[:limit]
    
    def _categorize_news(self, text: str) -> str:
        """Categorize news based on content."""
        text_lower = text.lower()
        
        # Count keyword matches for each category
        category_scores = {}
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            return max(category_scores.items(), key=lambda x: x[1])[0]
        
        return 'general'
    
    def _calculate_news_sentiment(
        self,
        title: str,
        content: str,
        category: str
    ) -> Dict[str, Any]:
        """Calculate sentiment from news content."""
        # Positive and negative keywords
        positive_keywords = [
            'success', 'growth', 'profit', 'gain', 'win', 'breakthrough',
            'innovative', 'partnership', 'expansion', 'milestone', 'record'
        ]
        negative_keywords = [
            'loss', 'decline', 'drop', 'fail', 'risk', 'concern', 'warning',
            'issue', 'problem', 'delay', 'cancel', 'fraud', 'scam'
        ]
        
        text = (title + ' ' + content).lower()
        
        positive_count = sum(1 for word in positive_keywords if word in text)
        negative_count = sum(1 for word in negative_keywords if word in text)
        
        # Consider category impact
        if category in self.news_categories:
            category_info = self.news_categories[category]
            if category_info['impact'] == 'positive':
                positive_count += 2
            else:
                negative_count += 2
        
        # Calculate score
        total = positive_count + negative_count
        if total == 0:
            score = 0.0
            sentiment = 'neutral'
        else:
            score = (positive_count - negative_count) / total
            if score > 0.2:
                sentiment = 'positive'
            elif score < -0.2:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'score': score,
            'positive_indicators': positive_count,
            'negative_indicators': negative_count
        }
    
    def _calculate_impact_score(
        self,
        category: str,
        source: str,
        sentiment: Dict[str, Any]
    ) -> float:
        """Calculate potential market impact of news."""
        # Base impact from category
        if category in self.news_categories:
            base_impact = self.news_categories[category]['weight']
        else:
            base_impact = 0.3
        
        # Adjust for source credibility
        trusted_sources = ['coindesk', 'cointelegraph', 'bloomberg', 'reuters']
        source_multiplier = 1.2 if any(s in source.lower() for s in trusted_sources) else 1.0
        
        # Adjust for sentiment strength
        sentiment_multiplier = 1.0 + abs(sentiment['score']) * 0.5
        
        impact = base_impact * source_multiplier * sentiment_multiplier
        
        return min(impact, 1.0)
    
    def _calculate_urgency(self, article: Dict[str, Any]) -> str:
        """Calculate urgency level of news."""
        age_minutes = (datetime.now() - article['publish_time']).total_seconds() / 60
        
        if age_minutes < 15 and article['impact_score'] > 0.8:
            return 'critical'
        elif age_minutes < 60 and article['impact_score'] > 0.6:
            return 'high'
        elif age_minutes < 360:
            return 'medium'
        else:
            return 'low'
    
    def _extract_tokens_from_text(self, text: str) -> List[str]:
        """Extract token symbols from text."""
        # Look for $SYMBOL or common token patterns
        token_pattern = r'\$([A-Z]{2,10})\b'
        tokens = re.findall(token_pattern, text.upper())
        
        # Common tokens
        common_tokens = ['BTC', 'ETH', 'USDT', 'USDC', 'BNB', 'SOL', 'ADA']
        for token in common_tokens:
            if token.lower() in text.lower() or token in text:
                tokens.append(token)
        
        return list(set(tokens))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get news processor statistics."""
        return {
            'total_articles_processed': len(self.news_articles),
            'tracked_tokens': len(self.token_news),
            'recent_articles_24h': sum(
                1 for article in self.news_articles
                if article['publish_time'] >= datetime.now() - timedelta(hours=24)
            ),
            'category_distribution': {
                category: sum(1 for a in self.news_articles if a['category'] == category)
                for category in self.news_categories.keys()
            }
        }
