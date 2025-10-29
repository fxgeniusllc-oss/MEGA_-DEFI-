"""Advanced Intelligence Layer - Integration of ML and Data Sources.

This module integrates ML components and data sources with the existing
strategy engine and market analyzer to provide enhanced decision-making.
"""

from typing import Dict, List, Any, Optional
import logging

from ..ml import (
    ReinforcementLearningOptimizer,
    DeepLearningPredictor,
    GeneticAlgorithmTuner,
    EnsembleModel
)
from ..data_sources import (
    MarketDataAggregator,
    WhaleTracker,
    SentimentAnalyzer,
    NewsProcessor,
    OnChainAnalytics
)

logger = logging.getLogger(__name__)


class IntelligenceLayer:
    """
    Advanced intelligence layer that integrates ML and data sources.
    
    Enhances trading decisions with:
    - Machine learning predictions
    - Real-time market data aggregation
    - Whale activity monitoring
    - Sentiment analysis
    - News impact assessment
    - On-chain analytics
    """
    
    def __init__(self, enable_ml: bool = True, enable_data_sources: bool = True):
        """
        Initialize the intelligence layer.
        
        Args:
            enable_ml: Enable ML components
            enable_data_sources: Enable data source integrations
        """
        self.enable_ml = enable_ml
        self.enable_data_sources = enable_data_sources
        
        # ML Components
        if enable_ml:
            self.rl_optimizer = ReinforcementLearningOptimizer()
            self.dl_predictor = DeepLearningPredictor()
            self.ga_tuner = GeneticAlgorithmTuner(population_size=30, max_generations=50)
            self.ensemble = EnsembleModel(voting_method='weighted')
            
            # Register models with ensemble
            self._register_ensemble_models()
        else:
            self.rl_optimizer = None
            self.dl_predictor = None
            self.ga_tuner = None
            self.ensemble = None
        
        # Data Sources
        if enable_data_sources:
            self.market_data = MarketDataAggregator()
            self.whale_tracker = WhaleTracker()
            self.sentiment = SentimentAnalyzer()
            self.news = NewsProcessor()
            self.onchain = OnChainAnalytics()
        else:
            self.market_data = None
            self.whale_tracker = None
            self.sentiment = None
            self.news = None
            self.onchain = None
        
        logger.info(
            f"Intelligence Layer initialized "
            f"(ML: {enable_ml}, Data Sources: {enable_data_sources})"
        )
    
    def enhance_market_analysis(
        self,
        base_analysis: Dict[str, Any],
        token: str
    ) -> Dict[str, Any]:
        """
        Enhance market analysis with ML predictions and data sources.
        
        Args:
            base_analysis: Base market analysis from MarketAnalyzer
            token: Token symbol
            
        Returns:
            Enhanced analysis with additional insights
        """
        enhanced = base_analysis.copy()
        
        # Add ML predictions
        if self.enable_ml:
            enhanced['ml_prediction'] = self._get_ml_prediction(base_analysis)
            enhanced['ensemble_signal'] = self._get_ensemble_signal(base_analysis)
        
        # Add data source insights
        if self.enable_data_sources:
            enhanced['whale_sentiment'] = self._get_whale_sentiment(token)
            enhanced['social_sentiment'] = self._get_social_sentiment(token)
            enhanced['news_sentiment'] = self._get_news_sentiment(token)
            enhanced['onchain_metrics'] = self._get_onchain_metrics(token)
        
        # Calculate composite score
        enhanced['composite_score'] = self._calculate_composite_score(enhanced)
        
        return enhanced
    
    def optimize_strategy_parameters(
        self,
        strategy_name: str,
        current_params: Dict[str, Any],
        market_data: Dict[str, Any],
        use_rl: bool = True,
        use_ga: bool = False
    ) -> Dict[str, Any]:
        """
        Optimize strategy parameters using ML.
        
        Args:
            strategy_name: Name of strategy
            current_params: Current parameters
            market_data: Market data
            use_rl: Use reinforcement learning
            use_ga: Use genetic algorithm
            
        Returns:
            Optimized parameters
        """
        if not self.enable_ml:
            return current_params
        
        optimized = current_params.copy()
        
        # RL optimization (fast, online learning)
        if use_rl and self.rl_optimizer:
            optimized = self.rl_optimizer.optimize_strategy_parameters(
                strategy_name,
                market_data,
                optimized
            )
        
        # GA optimization (slower, better for global optima)
        if use_ga and self.ga_tuner:
            # Define parameter ranges based on current values
            param_ranges = self._get_parameter_ranges(optimized)
            
            def fitness_func(params):
                # Simple fitness based on parameter values
                # In production, this would use backtesting
                return sum(params.values()) if params else 0
            
            optimized = self.ga_tuner.optimize(param_ranges, fitness_func)
        
        logger.debug(f"Optimized parameters for {strategy_name}: {optimized}")
        return optimized
    
    def process_trade_feedback(
        self,
        strategy_name: str,
        pre_trade_state: Dict[str, Any],
        action: str,
        result: Dict[str, Any],
        post_trade_state: Dict[str, Any]
    ) -> None:
        """
        Process feedback from completed trade for learning.
        
        Args:
            strategy_name: Strategy used
            pre_trade_state: State before trade
            action: Action taken
            result: Trade result
            post_trade_state: State after trade
        """
        if not self.enable_ml or not self.rl_optimizer:
            return
        
        # Update RL optimizer
        self.rl_optimizer.learn_from_trade(
            strategy_name,
            pre_trade_state,
            action,
            result,
            post_trade_state
        )
        
        # Update ensemble models
        if self.ensemble:
            success = result.get('success', False)
            # Update all models in ensemble
            for model_name in self.ensemble.models.keys():
                self.ensemble.update_model_performance(model_name, success)
    
    def track_market_event(
        self,
        event_type: str,
        token: str,
        data: Dict[str, Any]
    ) -> None:
        """
        Track a market event in data sources.
        
        Args:
            event_type: Type of event (transaction, news, etc.)
            token: Related token
            data: Event data
        """
        if not self.enable_data_sources:
            return
        
        if event_type == 'transaction':
            self._track_transaction(token, data)
        elif event_type == 'news':
            self._track_news(token, data)
        elif event_type == 'social_post':
            self._track_social_post(token, data)
    
    def get_comprehensive_insights(self, token: str) -> Dict[str, Any]:
        """
        Get comprehensive insights for a token.
        
        Args:
            token: Token symbol
            
        Returns:
            Comprehensive insights from all sources
        """
        insights = {
            'token': token,
            'ml_enabled': self.enable_ml,
            'data_sources_enabled': self.enable_data_sources
        }
        
        if self.enable_ml:
            insights['ml_performance'] = {
                'rl_metrics': self.rl_optimizer.get_performance_metrics() if self.rl_optimizer else {},
                'dl_metrics': self.dl_predictor.get_model_performance() if self.dl_predictor else {},
                'ensemble_metrics': self.ensemble.get_ensemble_metrics() if self.ensemble else {}
            }
        
        if self.enable_data_sources:
            insights['data_insights'] = {
                'whale_sentiment': self._get_whale_sentiment(token),
                'social_sentiment': self._get_social_sentiment(token),
                'news_sentiment': self._get_news_sentiment(token),
                'onchain_metrics': self._get_onchain_metrics(token)
            }
        
        return insights
    
    def _register_ensemble_models(self) -> None:
        """Register ML models with ensemble."""
        if not self.ensemble:
            return
        
        # Register deep learning predictor
        def dl_model(data):
            return self.dl_predictor.predict(data) if self.dl_predictor else {'signal': 'HOLD'}
        
        self.ensemble.register_model('deep_learning', dl_model, initial_weight=1.0)
    
    def _get_ml_prediction(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get ML prediction."""
        if self.dl_predictor:
            return self.dl_predictor.predict(market_data)
        return {'direction': 'neutral', 'confidence': 0.0}
    
    def _get_ensemble_signal(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get ensemble signal."""
        if self.ensemble:
            return self.ensemble.predict(market_data)
        return {'signal': 'HOLD', 'confidence': 0.0}
    
    def _get_whale_sentiment(self, token: str) -> Dict[str, Any]:
        """Get whale sentiment."""
        if self.whale_tracker:
            return self.whale_tracker.get_whale_sentiment(token)
        return {'sentiment': 'neutral', 'confidence': 0.0}
    
    def _get_social_sentiment(self, token: str) -> Dict[str, Any]:
        """Get social sentiment."""
        if self.sentiment:
            return self.sentiment.analyze_token_sentiment(token)
        return {'sentiment': 'neutral', 'score': 0.0}
    
    def _get_news_sentiment(self, token: str) -> Dict[str, Any]:
        """Get news sentiment."""
        if self.news:
            return self.news.get_token_news_sentiment(token)
        return {'sentiment': 'neutral', 'sentiment_score': 0.0}
    
    def _get_onchain_metrics(self, token: str) -> Dict[str, Any]:
        """Get on-chain metrics."""
        if self.onchain:
            flow = self.onchain.analyze_token_flow(token)
            velocity = self.onchain.calculate_velocity(token)
            return {
                'flow': flow,
                'velocity': velocity
            }
        return {'flow': {}, 'velocity': 0.0}
    
    def _calculate_composite_score(self, enhanced_analysis: Dict[str, Any]) -> float:
        """Calculate composite score from all sources."""
        score = 0.0
        weight_sum = 0.0
        
        # Base analysis
        if 'trend' in enhanced_analysis:
            score += enhanced_analysis['trend'] * 0.2
            weight_sum += 0.2
        
        # ML prediction
        if 'ml_prediction' in enhanced_analysis:
            ml_pred = enhanced_analysis['ml_prediction']
            direction_score = 0.0
            if ml_pred.get('direction') == 'up':
                direction_score = 1.0
            elif ml_pred.get('direction') == 'down':
                direction_score = -1.0
            
            score += direction_score * ml_pred.get('confidence', 0) * 0.3
            weight_sum += 0.3
        
        # Whale sentiment
        if 'whale_sentiment' in enhanced_analysis:
            whale = enhanced_analysis['whale_sentiment']
            sentiment_score = 0.0
            if whale.get('sentiment') == 'bullish':
                sentiment_score = 1.0
            elif whale.get('sentiment') == 'bearish':
                sentiment_score = -1.0
            
            score += sentiment_score * whale.get('confidence', 0) * 0.2
            weight_sum += 0.2
        
        # Social sentiment
        if 'social_sentiment' in enhanced_analysis:
            social = enhanced_analysis['social_sentiment']
            score += social.get('score', 0) * 0.15
            weight_sum += 0.15
        
        # News sentiment
        if 'news_sentiment' in enhanced_analysis:
            news = enhanced_analysis['news_sentiment']
            score += news.get('sentiment_score', 0) * 0.15
            weight_sum += 0.15
        
        # Normalize
        if weight_sum > 0:
            score = score / weight_sum
        
        return score
    
    def _track_transaction(self, token: str, data: Dict[str, Any]) -> None:
        """Track a transaction."""
        if self.whale_tracker:
            self.whale_tracker.track_transaction(
                data.get('tx_hash', ''),
                data.get('wallet', ''),
                token,
                data.get('amount', 0),
                data.get('value_usd', 0),
                data.get('type', 'buy')
            )
        
        if self.onchain:
            self.onchain.track_transfer(
                token,
                data.get('from', ''),
                data.get('to', ''),
                data.get('amount', 0),
                data.get('tx_hash', '')
            )
    
    def _track_news(self, token: str, data: Dict[str, Any]) -> None:
        """Track a news article."""
        if self.news:
            self.news.process_article(
                data.get('title', ''),
                data.get('content', ''),
                data.get('source', ''),
                [token]
            )
    
    def _track_social_post(self, token: str, data: Dict[str, Any]) -> None:
        """Track a social media post."""
        if self.sentiment:
            self.sentiment.track_post(
                data.get('text', ''),
                data.get('author', ''),
                data.get('source', ''),
                token
            )
    
    def _get_parameter_ranges(self, current_params: Dict[str, Any]) -> Dict[str, tuple]:
        """Get parameter ranges for optimization."""
        ranges = {}
        
        for param, value in current_params.items():
            if isinstance(value, (int, float)):
                # Create range around current value
                min_val = max(0.0, value * 0.5)
                max_val = value * 2.0
                ranges[param] = (min_val, max_val)
        
        return ranges
