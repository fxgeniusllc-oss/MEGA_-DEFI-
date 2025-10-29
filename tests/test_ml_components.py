"""Tests for Machine Learning Components."""

import unittest
from datetime import datetime, timedelta

from mega_defi.ml import (
    ReinforcementLearningOptimizer,
    DeepLearningPredictor,
    GeneticAlgorithmTuner,
    EnsembleModel
)


class TestReinforcementLearningOptimizer(unittest.TestCase):
    """Test cases for Reinforcement Learning Optimizer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.optimizer = ReinforcementLearningOptimizer(
            learning_rate=0.1,
            discount_factor=0.95,
            exploration_rate=0.3
        )
    
    def test_initialization(self):
        """Test optimizer initialization."""
        self.assertEqual(self.optimizer.learning_rate, 0.1)
        self.assertEqual(self.optimizer.discount_factor, 0.95)
        self.assertEqual(self.optimizer.exploration_rate, 0.3)
        self.assertEqual(len(self.optimizer.q_table), 0)
    
    def test_get_action(self):
        """Test action selection."""
        state = "low_medium_up"
        actions = ["increase_threshold", "decrease_threshold", "keep_threshold"]
        
        action = self.optimizer.get_action(state, actions)
        self.assertIn(action, actions)
    
    def test_update_q_values(self):
        """Test Q-value updates."""
        state = "low_medium_up"
        action = "increase_threshold"
        reward = 1.0
        next_state = "medium_low_down"
        next_actions = ["increase_threshold", "keep_threshold"]
        
        self.optimizer.update(state, action, reward, next_state, next_actions)
        
        # Check that Q-value was updated
        self.assertGreater(self.optimizer.q_table[state][action], 0)
        self.assertEqual(self.optimizer.training_steps, 1)
    
    def test_optimize_strategy_parameters(self):
        """Test strategy parameter optimization."""
        market_data = {
            'price': 100,
            'volatility': 0.2,
            'trend': 0.05
        }
        current_params = {
            'threshold': 0.01,
            'position_size': 0.1
        }
        
        optimized = self.optimizer.optimize_strategy_parameters(
            "test_strategy",
            market_data,
            current_params
        )
        
        self.assertIn('threshold', optimized)
        self.assertIn('position_size', optimized)
    
    def test_learn_from_trade(self):
        """Test learning from trade results."""
        pre_state = {'price': 100, 'volatility': 0.1, 'trend': 0.05}
        action = "increase_threshold"
        result = {'profit': 50, 'success': True}
        post_state = {'price': 105, 'volatility': 0.15, 'trend': 0.1}
        
        self.optimizer.learn_from_trade(
            "test_strategy",
            pre_state,
            action,
            result,
            post_state
        )
        
        self.assertEqual(len(self.optimizer.episode_rewards), 1)
        self.assertGreater(self.optimizer.episode_rewards[0], 0)
    
    def test_performance_metrics(self):
        """Test performance metrics retrieval."""
        metrics = self.optimizer.get_performance_metrics()
        
        self.assertIn('total_episodes', metrics)
        self.assertIn('average_reward', metrics)
        self.assertIn('training_steps', metrics)
        self.assertIn('exploration_rate', metrics)


class TestDeepLearningPredictor(unittest.TestCase):
    """Test cases for Deep Learning Predictor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.predictor = DeepLearningPredictor(
            input_size=10,
            hidden_size=20,
            output_size=3
        )
    
    def test_initialization(self):
        """Test predictor initialization."""
        self.assertEqual(self.predictor.input_size, 10)
        self.assertEqual(self.predictor.hidden_size, 20)
        self.assertEqual(self.predictor.output_size, 3)
        self.assertEqual(len(self.predictor.w1), 20)
        self.assertEqual(len(self.predictor.w2), 3)
    
    def test_predict(self):
        """Test market prediction."""
        market_data = {
            'price': 100,
            'volume': 50000,
            'volatility': 0.2,
            'trend': 0.05,
            'momentum': 0.1
        }
        
        prediction = self.predictor.predict(market_data)
        
        self.assertIn('direction', prediction)
        self.assertIn('confidence', prediction)
        self.assertIn('probabilities', prediction)
        self.assertIn(prediction['direction'], ['up', 'neutral', 'down'])
        self.assertGreaterEqual(prediction['confidence'], 0.0)
        self.assertLessEqual(prediction['confidence'], 1.0)
    
    def test_train(self):
        """Test model training."""
        training_data = [
            {'price': 100, 'volume': 50000, 'volatility': 0.2, 'trend': 0.05, 'momentum': 0.1}
            for _ in range(10)
        ]
        labels = [0, 1, 2, 0, 1, 2, 0, 1, 2, 0]  # up, neutral, down
        
        initial_losses_len = len(self.predictor.training_losses)
        self.predictor.train(training_data, labels, epochs=5)
        
        # Check that training occurred
        self.assertGreater(len(self.predictor.training_losses), initial_losses_len)
    
    def test_model_performance(self):
        """Test model performance metrics."""
        # Make some predictions
        market_data = {'price': 100, 'volume': 50000, 'volatility': 0.2}
        self.predictor.predict(market_data)
        
        performance = self.predictor.get_model_performance()
        
        self.assertIn('predictions_made', performance)
        self.assertIn('training_epochs', performance)
        self.assertEqual(performance['predictions_made'], 1)


class TestGeneticAlgorithmTuner(unittest.TestCase):
    """Test cases for Genetic Algorithm Tuner."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tuner = GeneticAlgorithmTuner(
            population_size=10,
            mutation_rate=0.1,
            max_generations=5
        )
    
    def test_initialization(self):
        """Test tuner initialization."""
        self.assertEqual(self.tuner.population_size, 10)
        self.assertEqual(self.tuner.mutation_rate, 0.1)
        self.assertEqual(self.tuner.max_generations, 5)
    
    def test_optimize(self):
        """Test parameter optimization."""
        # Simple fitness function: maximize sum of parameters
        def fitness_func(params):
            return sum(params.values())
        
        parameter_space = {
            'param1': (0.0, 1.0),
            'param2': (0.0, 1.0)
        }
        
        best_params = self.tuner.optimize(
            parameter_space,
            fitness_func,
            target_fitness=None
        )
        
        self.assertIn('param1', best_params)
        self.assertIn('param2', best_params)
        self.assertIsNotNone(self.tuner.best_fitness)
    
    def test_tune_strategy_parameters(self):
        """Test strategy parameter tuning."""
        def backtest_func(params):
            # Simple fitness: higher threshold = better
            return params.get('threshold', 0) * 100
        
        param_ranges = {
            'threshold': (0.001, 0.1),
            'stop_loss': (0.01, 0.2)
        }
        
        optimized = self.tuner.tune_strategy_parameters(
            "test_strategy",
            param_ranges,
            backtest_func
        )
        
        self.assertIn('threshold', optimized)
        self.assertIn('stop_loss', optimized)
    
    def test_optimization_report(self):
        """Test optimization report generation."""
        # Run simple optimization first
        def fitness_func(params):
            return params.get('param1', 0)
        
        parameter_space = {'param1': (0.0, 1.0)}
        self.tuner.optimize(parameter_space, fitness_func)
        
        report = self.tuner.get_optimization_report()
        
        self.assertEqual(report['status'], 'complete')
        self.assertIn('best_fitness', report)
        self.assertIn('best_parameters', report)
        self.assertIn('generations_run', report)


class TestEnsembleModel(unittest.TestCase):
    """Test cases for Ensemble Model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.ensemble = EnsembleModel(
            voting_method='weighted',
            min_consensus=0.6
        )
    
    def test_initialization(self):
        """Test ensemble initialization."""
        self.assertEqual(self.ensemble.voting_method, 'weighted')
        self.assertEqual(self.ensemble.min_consensus, 0.6)
        self.assertEqual(len(self.ensemble.models), 0)
    
    def test_register_model(self):
        """Test model registration."""
        def dummy_model(data):
            return {'signal': 'BUY', 'confidence': 0.8}
        
        self.ensemble.register_model('model1', dummy_model, initial_weight=1.0)
        
        self.assertIn('model1', self.ensemble.models)
        self.assertEqual(self.ensemble.model_weights['model1'], 1.0)
    
    def test_predict_with_multiple_models(self):
        """Test ensemble prediction."""
        # Register multiple models
        def model1(data):
            return {'signal': 'BUY', 'confidence': 0.8}
        
        def model2(data):
            return {'signal': 'BUY', 'confidence': 0.7}
        
        def model3(data):
            return {'signal': 'SELL', 'confidence': 0.6}
        
        self.ensemble.register_model('model1', model1)
        self.ensemble.register_model('model2', model2)
        self.ensemble.register_model('model3', model3)
        
        prediction = self.ensemble.predict({'price': 100})
        
        self.assertIn('signal', prediction)
        self.assertIn('confidence', prediction)
        self.assertIn('consensus', prediction)
        self.assertEqual(len(prediction['model_predictions']), 3)
    
    def test_aggregate_signals(self):
        """Test signal aggregation."""
        signals = [
            {'action': 'BUY', 'strength': 0.8},
            {'action': 'BUY', 'strength': 0.7},
            {'action': 'SELL', 'strength': 0.5}
        ]
        
        aggregated = self.ensemble.aggregate_signals(signals)
        
        self.assertIn('action', aggregated)
        self.assertIn('strength', aggregated)
        self.assertEqual(aggregated['action'], 'BUY')
    
    def test_update_model_performance(self):
        """Test model performance tracking."""
        def dummy_model(data):
            return {'signal': 'BUY'}
        
        self.ensemble.register_model('model1', dummy_model)
        
        # Update performance
        self.ensemble.update_model_performance('model1', True)
        self.ensemble.update_model_performance('model1', False)
        
        perf = self.ensemble.model_performance['model1']
        self.assertEqual(perf['total'], 2)
        self.assertEqual(perf['correct'], 1)
    
    def test_ensemble_metrics(self):
        """Test ensemble metrics."""
        def dummy_model(data):
            return {'signal': 'BUY', 'confidence': 0.8}
        
        self.ensemble.register_model('model1', dummy_model)
        self.ensemble.predict({'price': 100})
        
        metrics = self.ensemble.get_ensemble_metrics()
        
        self.assertIn('total_predictions', metrics)
        self.assertIn('model_count', metrics)
        self.assertIn('average_confidence', metrics)


if __name__ == '__main__':
    unittest.main()
