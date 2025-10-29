"""Reinforcement Learning Optimizer for Strategy Optimization.

This module implements a Q-Learning based approach to optimize trading strategies
by learning from market feedback and maximizing cumulative rewards.
"""

from typing import Dict, List, Any, Tuple
import logging
from collections import defaultdict
import random

logger = logging.getLogger(__name__)


class ReinforcementLearningOptimizer:
    """
    Reinforcement Learning optimizer using Q-Learning for strategy optimization.
    
    Uses Q-Learning to learn optimal strategy parameters based on market conditions
    and historical performance.
    """
    
    def __init__(
        self,
        learning_rate: float = 0.1,
        discount_factor: float = 0.95,
        exploration_rate: float = 0.2,
        min_exploration: float = 0.01,
        exploration_decay: float = 0.995
    ):
        """
        Initialize the RL optimizer.
        
        Args:
            learning_rate: Learning rate (alpha) for Q-learning
            discount_factor: Discount factor (gamma) for future rewards
            exploration_rate: Initial exploration rate (epsilon)
            min_exploration: Minimum exploration rate
            exploration_decay: Decay rate for exploration
        """
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.min_exploration = min_exploration
        self.exploration_decay = exploration_decay
        
        # Q-table: state -> action -> Q-value
        self.q_table = defaultdict(lambda: defaultdict(float))
        
        # Performance tracking
        self.episode_rewards = []
        self.training_steps = 0
        
        logger.info("Reinforcement Learning Optimizer initialized")
    
    def get_action(self, state: str, available_actions: List[str]) -> str:
        """
        Select an action using epsilon-greedy policy.
        
        Args:
            state: Current market state
            available_actions: List of available actions
            
        Returns:
            Selected action
        """
        # Exploration: random action
        if random.random() < self.exploration_rate:
            return random.choice(available_actions)
        
        # Exploitation: best known action
        q_values = {action: self.q_table[state][action] for action in available_actions}
        max_q = max(q_values.values()) if q_values else 0
        
        # Get all actions with max Q-value (for tie-breaking)
        best_actions = [action for action, q in q_values.items() if q == max_q]
        return random.choice(best_actions)
    
    def update(
        self,
        state: str,
        action: str,
        reward: float,
        next_state: str,
        available_next_actions: List[str]
    ) -> None:
        """
        Update Q-values based on experience.
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            available_next_actions: Available actions in next state
        """
        # Get current Q-value
        current_q = self.q_table[state][action]
        
        # Get max Q-value for next state
        if available_next_actions:
            next_q_values = [self.q_table[next_state][a] for a in available_next_actions]
            max_next_q = max(next_q_values) if next_q_values else 0
        else:
            max_next_q = 0
        
        # Q-learning update
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )
        
        self.q_table[state][action] = new_q
        self.training_steps += 1
        
        # Decay exploration rate
        self.exploration_rate = max(
            self.min_exploration,
            self.exploration_rate * self.exploration_decay
        )
    
    def optimize_strategy_parameters(
        self,
        strategy_name: str,
        market_data: Dict[str, Any],
        current_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimize strategy parameters using learned Q-values.
        
        Args:
            strategy_name: Name of the strategy
            market_data: Current market conditions
            current_params: Current strategy parameters
            
        Returns:
            Optimized parameters
        """
        # Create state representation
        state = self._create_state_representation(market_data)
        
        # Get available parameter adjustments
        actions = self._get_parameter_actions(strategy_name, current_params)
        
        # Select best action
        if actions:
            best_action = self.get_action(state, actions)
            optimized_params = self._apply_action(current_params, best_action)
        else:
            optimized_params = current_params.copy()
        
        logger.debug(f"Optimized parameters for {strategy_name}: {optimized_params}")
        return optimized_params
    
    def learn_from_trade(
        self,
        strategy_name: str,
        pre_trade_state: Dict[str, Any],
        action_taken: str,
        trade_result: Dict[str, Any],
        post_trade_state: Dict[str, Any]
    ) -> None:
        """
        Learn from a completed trade.
        
        Args:
            strategy_name: Name of strategy used
            pre_trade_state: Market state before trade
            action_taken: Action that was taken
            trade_result: Result of the trade (profit/loss)
            post_trade_state: Market state after trade
        """
        # Calculate reward
        profit = trade_result.get('profit', 0)
        success = trade_result.get('success', False)
        
        # Reward function: profit-based with success bonus
        reward = profit / 100.0  # Normalize profit
        if success:
            reward += 1.0  # Bonus for successful trade
        else:
            reward -= 0.5  # Penalty for failed trade
        
        # Create state representations
        state = self._create_state_representation(pre_trade_state)
        next_state = self._create_state_representation(post_trade_state)
        
        # Get available actions
        available_actions = self._get_parameter_actions(
            strategy_name,
            pre_trade_state.get('params', {})
        )
        
        # Update Q-values
        self.update(state, action_taken, reward, next_state, available_actions)
        
        # Track episode reward
        self.episode_rewards.append(reward)
        
        logger.debug(f"Learned from trade: reward={reward:.4f}, exploration={self.exploration_rate:.4f}")
    
    def _create_state_representation(self, market_data: Dict[str, Any]) -> str:
        """Create a discrete state representation from market data."""
        # Discretize continuous values
        price = market_data.get('price', 0)
        volatility = market_data.get('volatility', 0)
        trend = market_data.get('trend', 0)
        
        # Create buckets
        price_bucket = "low" if price < 100 else "medium" if price < 1000 else "high"
        vol_bucket = "low" if volatility < 0.1 else "medium" if volatility < 0.3 else "high"
        trend_bucket = "down" if trend < -0.05 else "neutral" if trend < 0.05 else "up"
        
        return f"{price_bucket}_{vol_bucket}_{trend_bucket}"
    
    def _get_parameter_actions(
        self,
        strategy_name: str,
        current_params: Dict[str, Any]
    ) -> List[str]:
        """Get available parameter adjustment actions."""
        actions = []
        
        # Generic parameter adjustments
        if 'threshold' in current_params:
            actions.extend(['increase_threshold', 'decrease_threshold', 'keep_threshold'])
        
        if 'position_size' in current_params:
            actions.extend(['increase_size', 'decrease_size', 'keep_size'])
        
        if 'stop_loss' in current_params:
            actions.extend(['tighten_stop', 'loosen_stop', 'keep_stop'])
        
        # Default action
        if not actions:
            actions.append('no_change')
        
        return actions
    
    def _apply_action(
        self,
        params: Dict[str, Any],
        action: str
    ) -> Dict[str, Any]:
        """Apply a parameter adjustment action."""
        new_params = params.copy()
        
        # Threshold adjustments
        if action == 'increase_threshold' and 'threshold' in new_params:
            new_params['threshold'] = min(new_params['threshold'] * 1.1, 1.0)
        elif action == 'decrease_threshold' and 'threshold' in new_params:
            new_params['threshold'] = max(new_params['threshold'] * 0.9, 0.001)
        
        # Position size adjustments
        elif action == 'increase_size' and 'position_size' in new_params:
            new_params['position_size'] = min(new_params['position_size'] * 1.1, 1.0)
        elif action == 'decrease_size' and 'position_size' in new_params:
            new_params['position_size'] = max(new_params['position_size'] * 0.9, 0.01)
        
        # Stop loss adjustments
        elif action == 'tighten_stop' and 'stop_loss' in new_params:
            new_params['stop_loss'] = max(new_params['stop_loss'] * 0.9, 0.01)
        elif action == 'loosen_stop' and 'stop_loss' in new_params:
            new_params['stop_loss'] = min(new_params['stop_loss'] * 1.1, 0.2)
        
        return new_params
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics of the RL optimizer."""
        if not self.episode_rewards:
            return {
                'total_episodes': 0,
                'average_reward': 0,
                'training_steps': self.training_steps,
                'exploration_rate': self.exploration_rate
            }
        
        return {
            'total_episodes': len(self.episode_rewards),
            'average_reward': sum(self.episode_rewards) / len(self.episode_rewards),
            'recent_average': sum(self.episode_rewards[-100:]) / min(100, len(self.episode_rewards)),
            'training_steps': self.training_steps,
            'exploration_rate': self.exploration_rate,
            'q_table_size': len(self.q_table)
        }
