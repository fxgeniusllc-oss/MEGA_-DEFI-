"""Ensemble Model for Signal Aggregation.

This module implements ensemble learning to aggregate signals from multiple
sources and strategies for more robust predictions.
"""

from typing import Dict, List, Any, Callable
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class EnsembleModel:
    """
    Ensemble model that combines multiple prediction sources.
    
    Uses weighted voting and consensus methods to aggregate signals from:
    - Multiple strategies
    - Different ML models
    - Various technical indicators
    """
    
    def __init__(
        self,
        voting_method: str = 'weighted',
        min_consensus: float = 0.6,
        dynamic_weights: bool = True
    ):
        """
        Initialize the ensemble model.
        
        Args:
            voting_method: Method for combining signals ('weighted', 'majority', 'unanimous')
            min_consensus: Minimum consensus required for strong signal
            dynamic_weights: Whether to adjust weights based on performance
        """
        self.voting_method = voting_method
        self.min_consensus = min_consensus
        self.dynamic_weights = dynamic_weights
        
        # Model registry
        self.models = {}
        self.model_weights = {}
        self.model_performance = defaultdict(lambda: {'correct': 0, 'total': 0})
        
        # Prediction history
        self.predictions = []
        self.ensemble_accuracy = 0.0
        
        logger.info("Ensemble Model initialized")
    
    def register_model(
        self,
        model_name: str,
        model_function: Callable[[Dict[str, Any]], Dict[str, Any]],
        initial_weight: float = 1.0
    ) -> None:
        """
        Register a model or strategy to the ensemble.
        
        Args:
            model_name: Unique name for the model
            model_function: Function that returns predictions
            initial_weight: Initial weight for voting
        """
        self.models[model_name] = model_function
        self.model_weights[model_name] = initial_weight
        logger.info(f"Registered model: {model_name} with weight {initial_weight}")
    
    def predict(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate ensemble prediction from all models.
        
        Args:
            market_data: Current market data
            
        Returns:
            Aggregated prediction with confidence and consensus
        """
        if not self.models:
            logger.warning("No models registered for ensemble prediction")
            return {
                'signal': 'HOLD',
                'confidence': 0.0,
                'consensus': 0.0,
                'model_predictions': {}
            }
        
        # Collect predictions from all models
        model_predictions = {}
        
        for model_name, model_func in self.models.items():
            try:
                prediction = model_func(market_data)
                model_predictions[model_name] = prediction
            except Exception as e:
                logger.error(f"Error getting prediction from {model_name}: {e}")
                continue
        
        # Aggregate predictions
        if self.voting_method == 'weighted':
            ensemble_signal = self._weighted_voting(model_predictions)
        elif self.voting_method == 'majority':
            ensemble_signal = self._majority_voting(model_predictions)
        elif self.voting_method == 'unanimous':
            ensemble_signal = self._unanimous_voting(model_predictions)
        else:
            ensemble_signal = self._weighted_voting(model_predictions)
        
        # Calculate consensus
        consensus = self._calculate_consensus(model_predictions)
        
        # Determine final signal and confidence
        final_signal = ensemble_signal['signal']
        confidence = ensemble_signal['confidence'] * consensus
        
        # Store prediction
        prediction_result = {
            'signal': final_signal,
            'confidence': confidence,
            'consensus': consensus,
            'model_predictions': model_predictions,
            'voting_method': self.voting_method,
            'meets_consensus': consensus >= self.min_consensus
        }
        
        self.predictions.append(prediction_result)
        
        logger.debug(
            f"Ensemble prediction: {final_signal} "
            f"(confidence={confidence:.2%}, consensus={consensus:.2%})"
        )
        
        return prediction_result
    
    def aggregate_signals(
        self,
        signals: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Aggregate multiple trading signals.
        
        Args:
            signals: List of signal dictionaries from different sources
            
        Returns:
            Aggregated signal
        """
        if not signals:
            return {'action': 'HOLD', 'strength': 0.0}
        
        # Count signal types
        signal_counts = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
        total_strength = 0.0
        
        for signal in signals:
            action = signal.get('action', 'HOLD')
            strength = signal.get('strength', 1.0)
            
            if action in signal_counts:
                signal_counts[action] += strength
                total_strength += strength
        
        # Determine dominant signal
        dominant_signal = max(signal_counts.items(), key=lambda x: x[1])
        
        return {
            'action': dominant_signal[0],
            'strength': dominant_signal[1] / total_strength if total_strength > 0 else 0.0,
            'distribution': signal_counts,
            'total_signals': len(signals)
        }
    
    def update_model_performance(
        self,
        model_name: str,
        was_correct: bool
    ) -> None:
        """
        Update model performance tracking.
        
        Args:
            model_name: Name of the model
            was_correct: Whether the prediction was correct
        """
        if model_name not in self.models:
            logger.warning(f"Unknown model: {model_name}")
            return
        
        perf = self.model_performance[model_name]
        perf['total'] += 1
        if was_correct:
            perf['correct'] += 1
        
        # Update weights if dynamic weighting is enabled
        if self.dynamic_weights:
            self._update_weights()
        
        logger.debug(f"Updated {model_name} performance: {perf['correct']}/{perf['total']}")
    
    def _weighted_voting(self, predictions: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate predictions using weighted voting."""
        signal_scores = {'BUY': 0.0, 'SELL': 0.0, 'HOLD': 0.0}
        total_weight = 0.0
        
        for model_name, pred in predictions.items():
            weight = self.model_weights.get(model_name, 1.0)
            signal = pred.get('signal', pred.get('direction', 'HOLD')).upper()
            confidence = pred.get('confidence', 1.0)
            
            if signal in signal_scores:
                signal_scores[signal] += weight * confidence
                total_weight += weight
        
        # Get winning signal
        if total_weight > 0:
            winning_signal = max(signal_scores.items(), key=lambda x: x[1])
            confidence = winning_signal[1] / total_weight
        else:
            winning_signal = ('HOLD', 0.0)
            confidence = 0.0
        
        return {
            'signal': winning_signal[0],
            'confidence': confidence,
            'scores': signal_scores
        }
    
    def _majority_voting(self, predictions: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate predictions using simple majority voting."""
        signal_counts = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
        
        for pred in predictions.values():
            signal = pred.get('signal', pred.get('direction', 'HOLD')).upper()
            if signal in signal_counts:
                signal_counts[signal] += 1
        
        winning_signal = max(signal_counts.items(), key=lambda x: x[1])
        total_votes = sum(signal_counts.values())
        
        return {
            'signal': winning_signal[0],
            'confidence': winning_signal[1] / total_votes if total_votes > 0 else 0.0,
            'scores': signal_counts
        }
    
    def _unanimous_voting(self, predictions: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Require unanimous agreement for non-HOLD signals."""
        signals = set()
        
        for pred in predictions.values():
            signal = pred.get('signal', pred.get('direction', 'HOLD')).upper()
            signals.add(signal)
        
        # If all agree, use that signal, otherwise HOLD
        if len(signals) == 1:
            signal = list(signals)[0]
            confidence = 1.0
        else:
            signal = 'HOLD'
            confidence = 0.0
        
        return {
            'signal': signal,
            'confidence': confidence,
            'scores': {'unanimous': len(signals) == 1}
        }
    
    def _calculate_consensus(self, predictions: Dict[str, Dict[str, Any]]) -> float:
        """Calculate consensus level among predictions."""
        if not predictions:
            return 0.0
        
        # Count each signal type
        signal_counts = defaultdict(int)
        
        for pred in predictions.values():
            signal = pred.get('signal', pred.get('direction', 'HOLD')).upper()
            signal_counts[signal] += 1
        
        # Consensus is the proportion of the most common signal
        max_count = max(signal_counts.values())
        consensus = max_count / len(predictions)
        
        return consensus
    
    def _update_weights(self) -> None:
        """Update model weights based on performance."""
        for model_name in self.models.keys():
            perf = self.model_performance[model_name]
            
            if perf['total'] > 0:
                accuracy = perf['correct'] / perf['total']
                # Weight is proportional to accuracy
                # Minimum weight of 0.1 to give all models a chance
                self.model_weights[model_name] = max(0.1, accuracy)
    
    def get_ensemble_metrics(self) -> Dict[str, Any]:
        """Get ensemble performance metrics."""
        if not self.predictions:
            return {
                'total_predictions': 0,
                'average_confidence': 0.0,
                'average_consensus': 0.0,
                'model_count': len(self.models)
            }
        
        return {
            'total_predictions': len(self.predictions),
            'average_confidence': sum(p['confidence'] for p in self.predictions) / len(self.predictions),
            'average_consensus': sum(p['consensus'] for p in self.predictions) / len(self.predictions),
            'model_count': len(self.models),
            'model_weights': self.model_weights.copy(),
            'model_performance': {
                name: {
                    'accuracy': perf['correct'] / perf['total'] if perf['total'] > 0 else 0.0,
                    'total_predictions': perf['total']
                }
                for name, perf in self.model_performance.items()
            },
            'voting_method': self.voting_method
        }
