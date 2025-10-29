"""Deep Learning Market Predictor.

This module implements a neural network-based approach to predict market movements
using historical price and market data.
"""

from typing import Dict, List, Any, Optional
import logging
import math

logger = logging.getLogger(__name__)


class DeepLearningPredictor:
    """
    Deep Learning predictor for market prediction using a simple neural network.
    
    Implements a feedforward neural network for price prediction without external dependencies.
    """
    
    def __init__(
        self,
        input_size: int = 10,
        hidden_size: int = 20,
        output_size: int = 3,
        learning_rate: float = 0.01
    ):
        """
        Initialize the deep learning predictor.
        
        Args:
            input_size: Number of input features
            hidden_size: Number of hidden layer neurons
            output_size: Number of output classes (up/down/neutral)
            learning_rate: Learning rate for training
        """
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.learning_rate = learning_rate
        
        # Initialize weights with small random values
        self.w1 = [[self._random_weight() for _ in range(input_size)] for _ in range(hidden_size)]
        self.b1 = [0.0 for _ in range(hidden_size)]
        
        self.w2 = [[self._random_weight() for _ in range(hidden_size)] for _ in range(output_size)]
        self.b2 = [0.0 for _ in range(output_size)]
        
        # Training history
        self.training_losses = []
        self.predictions_made = 0
        
        logger.info("Deep Learning Predictor initialized")
    
    def _random_weight(self) -> float:
        """Generate random weight using Xavier initialization."""
        import random
        return random.uniform(-0.1, 0.1)
    
    def _sigmoid(self, x: float) -> float:
        """Sigmoid activation function."""
        try:
            return 1.0 / (1.0 + math.exp(-x))
        except OverflowError:
            return 0.0 if x < 0 else 1.0
    
    def _relu(self, x: float) -> float:
        """ReLU activation function."""
        return max(0.0, x)
    
    def _softmax(self, x: List[float]) -> List[float]:
        """Softmax activation for output layer."""
        # Subtract max for numerical stability
        max_x = max(x)
        exp_x = [math.exp(xi - max_x) for xi in x]
        sum_exp = sum(exp_x)
        return [e / sum_exp if sum_exp > 0 else 1.0 / len(x) for e in exp_x]
    
    def _forward_pass(self, inputs: List[float]) -> tuple:
        """
        Perform forward pass through the network.
        
        Returns:
            (hidden_activations, output_probabilities)
        """
        # Hidden layer
        hidden = []
        for i in range(self.hidden_size):
            activation = sum(inputs[j] * self.w1[i][j] for j in range(len(inputs)))
            activation += self.b1[i]
            hidden.append(self._relu(activation))
        
        # Output layer
        output = []
        for i in range(self.output_size):
            activation = sum(hidden[j] * self.w2[i][j] for j in range(len(hidden)))
            activation += self.b2[i]
            output.append(activation)
        
        # Apply softmax
        output_probs = self._softmax(output)
        
        return hidden, output_probs
    
    def predict(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict market direction based on current data.
        
        Args:
            market_data: Dictionary containing market features
            
        Returns:
            Prediction results with probabilities and direction
        """
        # Extract and normalize features
        features = self._extract_features(market_data)
        
        # Forward pass
        _, output_probs = self._forward_pass(features)
        
        # Interpret output
        prediction = {
            'direction': self._get_direction(output_probs),
            'confidence': max(output_probs),
            'probabilities': {
                'up': output_probs[0],
                'neutral': output_probs[1],
                'down': output_probs[2]
            },
            'expected_return': self._calculate_expected_return(output_probs)
        }
        
        self.predictions_made += 1
        logger.debug(f"Prediction: {prediction['direction']} with {prediction['confidence']:.2%} confidence")
        
        return prediction
    
    def train(
        self,
        training_data: List[Dict[str, Any]],
        labels: List[int],
        epochs: int = 100
    ) -> None:
        """
        Train the network on historical data.
        
        Args:
            training_data: List of market data points
            labels: Corresponding labels (0=up, 1=neutral, 2=down)
            epochs: Number of training epochs
        """
        for epoch in range(epochs):
            total_loss = 0.0
            
            for data, label in zip(training_data, labels):
                features = self._extract_features(data)
                
                # Forward pass
                hidden, output = self._forward_pass(features)
                
                # Calculate loss (cross-entropy)
                target = [1.0 if i == label else 0.0 for i in range(self.output_size)]
                loss = -sum(t * math.log(o + 1e-10) for t, o in zip(target, output))
                total_loss += loss
                
                # Backward pass (simplified gradient descent)
                self._backward_pass(features, hidden, output, target)
            
            avg_loss = total_loss / len(training_data)
            self.training_losses.append(avg_loss)
            
            if epoch % 10 == 0:
                logger.debug(f"Epoch {epoch}: loss={avg_loss:.4f}")
    
    def _backward_pass(
        self,
        inputs: List[float],
        hidden: List[float],
        output: List[float],
        target: List[float]
    ) -> None:
        """Perform backward pass and update weights."""
        # Output layer gradients
        output_errors = [output[i] - target[i] for i in range(self.output_size)]
        
        # Update output layer weights
        for i in range(self.output_size):
            for j in range(self.hidden_size):
                gradient = output_errors[i] * hidden[j]
                self.w2[i][j] -= self.learning_rate * gradient
            self.b2[i] -= self.learning_rate * output_errors[i]
        
        # Hidden layer gradients
        hidden_errors = []
        for j in range(self.hidden_size):
            error = sum(output_errors[i] * self.w2[i][j] for i in range(self.output_size))
            # ReLU derivative
            if hidden[j] > 0:
                hidden_errors.append(error)
            else:
                hidden_errors.append(0.0)
        
        # Update hidden layer weights
        for i in range(self.hidden_size):
            for j in range(len(inputs)):
                gradient = hidden_errors[i] * inputs[j]
                self.w1[i][j] -= self.learning_rate * gradient
            self.b1[i] -= self.learning_rate * hidden_errors[i]
    
    def _extract_features(self, market_data: Dict[str, Any]) -> List[float]:
        """Extract and normalize features from market data."""
        features = []
        
        # Price-based features
        features.append(self._normalize(market_data.get('price', 0), 0, 10000))
        features.append(self._normalize(market_data.get('volume', 0), 0, 1000000))
        features.append(self._normalize(market_data.get('volatility', 0), 0, 1))
        features.append(self._normalize(market_data.get('trend', 0), -1, 1))
        features.append(self._normalize(market_data.get('momentum', 0), -1, 1))
        
        # Technical indicators
        features.append(self._normalize(market_data.get('rsi', 50), 0, 100))
        features.append(self._normalize(market_data.get('macd', 0), -100, 100))
        features.append(self._normalize(market_data.get('liquidity', 0), 0, 10000000))
        
        # Additional features
        features.append(self._normalize(market_data.get('price_deviation', 0), -1, 1))
        features.append(self._normalize(market_data.get('trend_strength', 0), 0, 1))
        
        # Pad or truncate to input_size
        while len(features) < self.input_size:
            features.append(0.0)
        
        return features[:self.input_size]
    
    def _normalize(self, value: float, min_val: float, max_val: float) -> float:
        """Normalize value to [0, 1] range."""
        if max_val == min_val:
            return 0.5
        return max(0.0, min(1.0, (value - min_val) / (max_val - min_val)))
    
    def _get_direction(self, probabilities: List[float]) -> str:
        """Get direction from probability distribution."""
        max_idx = probabilities.index(max(probabilities))
        return ['up', 'neutral', 'down'][max_idx]
    
    def _calculate_expected_return(self, probabilities: List[float]) -> float:
        """Calculate expected return based on probabilities."""
        # Assume: up=+2%, neutral=0%, down=-2%
        expected = probabilities[0] * 0.02 + probabilities[1] * 0.0 + probabilities[2] * -0.02
        return expected
    
    def get_model_performance(self) -> Dict[str, Any]:
        """Get model performance metrics."""
        return {
            'predictions_made': self.predictions_made,
            'training_epochs': len(self.training_losses),
            'final_loss': self.training_losses[-1] if self.training_losses else 0.0,
            'average_loss': sum(self.training_losses) / len(self.training_losses) if self.training_losses else 0.0,
            'model_parameters': {
                'input_size': self.input_size,
                'hidden_size': self.hidden_size,
                'output_size': self.output_size
            }
        }
