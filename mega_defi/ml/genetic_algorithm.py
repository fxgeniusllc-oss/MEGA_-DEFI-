"""Genetic Algorithm for Parameter Tuning.

This module implements a genetic algorithm to evolve and optimize strategy parameters
through natural selection and mutation.
"""

from typing import Dict, List, Any, Callable, Optional
import logging
import random
import copy

logger = logging.getLogger(__name__)


class GeneticAlgorithmTuner:
    """
    Genetic Algorithm optimizer for strategy parameter tuning.
    
    Uses evolutionary algorithms to find optimal parameter combinations by:
    - Creating a population of parameter sets
    - Evaluating fitness based on performance
    - Selecting best performers
    - Crossover and mutation to create new generations
    """
    
    def __init__(
        self,
        population_size: int = 50,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.7,
        elite_size: int = 5,
        max_generations: int = 100
    ):
        """
        Initialize the genetic algorithm tuner.
        
        Args:
            population_size: Number of individuals in population
            mutation_rate: Probability of mutation
            crossover_rate: Probability of crossover
            elite_size: Number of top performers to keep
            max_generations: Maximum number of generations
        """
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_size = elite_size
        self.max_generations = max_generations
        
        self.population = []
        self.best_individual = None
        self.best_fitness = float('-inf')
        self.generation = 0
        self.fitness_history = []
        
        logger.info("Genetic Algorithm Tuner initialized")
    
    def optimize(
        self,
        parameter_space: Dict[str, tuple],
        fitness_function: Callable[[Dict[str, Any]], float],
        target_fitness: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Optimize parameters using genetic algorithm.
        
        Args:
            parameter_space: Dictionary mapping parameter names to (min, max) ranges
            fitness_function: Function that evaluates parameter fitness
            target_fitness: Optional target fitness to stop early
            
        Returns:
            Best parameters found
        """
        # Initialize population
        self.population = self._initialize_population(parameter_space)
        
        for generation in range(self.max_generations):
            self.generation = generation
            
            # Evaluate fitness
            fitness_scores = []
            for individual in self.population:
                fitness = fitness_function(individual)
                fitness_scores.append(fitness)
                
                # Track best individual
                if fitness > self.best_fitness:
                    self.best_fitness = fitness
                    self.best_individual = copy.deepcopy(individual)
            
            # Record generation statistics
            avg_fitness = sum(fitness_scores) / len(fitness_scores)
            self.fitness_history.append({
                'generation': generation,
                'best': max(fitness_scores),
                'average': avg_fitness,
                'worst': min(fitness_scores)
            })
            
            logger.debug(f"Generation {generation}: best={max(fitness_scores):.4f}, avg={avg_fitness:.4f}")
            
            # Check if target reached
            if target_fitness and max(fitness_scores) >= target_fitness:
                logger.info(f"Target fitness {target_fitness} reached at generation {generation}")
                break
            
            # Create next generation
            self.population = self._evolve_population(
                self.population,
                fitness_scores,
                parameter_space
            )
        
        logger.info(f"Optimization complete. Best fitness: {self.best_fitness:.4f}")
        return self.best_individual
    
    def tune_strategy_parameters(
        self,
        strategy_name: str,
        parameter_ranges: Dict[str, tuple],
        backtest_function: Callable[[Dict[str, Any]], float]
    ) -> Dict[str, Any]:
        """
        Tune strategy parameters for optimal performance.
        
        Args:
            strategy_name: Name of the strategy
            parameter_ranges: Dictionary of parameter ranges
            backtest_function: Function to evaluate parameter performance
            
        Returns:
            Optimized parameters
        """
        logger.info(f"Tuning parameters for {strategy_name}")
        
        def fitness_wrapper(params: Dict[str, Any]) -> float:
            """Wrapper to evaluate strategy performance."""
            try:
                return backtest_function(params)
            except Exception as e:
                logger.error(f"Error evaluating parameters: {e}")
                return float('-inf')
        
        optimized = self.optimize(parameter_ranges, fitness_wrapper)
        
        logger.info(f"Optimized {strategy_name} parameters: {optimized}")
        return optimized
    
    def _initialize_population(self, parameter_space: Dict[str, tuple]) -> List[Dict[str, Any]]:
        """Initialize random population within parameter space."""
        population = []
        
        for _ in range(self.population_size):
            individual = {}
            for param_name, (min_val, max_val) in parameter_space.items():
                # Generate random value in range
                if isinstance(min_val, int) and isinstance(max_val, int):
                    individual[param_name] = random.randint(min_val, max_val)
                else:
                    individual[param_name] = random.uniform(min_val, max_val)
            
            population.append(individual)
        
        return population
    
    def _evolve_population(
        self,
        population: List[Dict[str, Any]],
        fitness_scores: List[float],
        parameter_space: Dict[str, tuple]
    ) -> List[Dict[str, Any]]:
        """Create next generation through selection, crossover, and mutation."""
        # Combine population with fitness
        scored_population = list(zip(population, fitness_scores))
        scored_population.sort(key=lambda x: x[1], reverse=True)
        
        # Elite selection - keep best performers
        new_population = [ind for ind, _ in scored_population[:self.elite_size]]
        
        # Generate offspring
        while len(new_population) < self.population_size:
            # Tournament selection
            parent1 = self._tournament_selection(scored_population)
            parent2 = self._tournament_selection(scored_population)
            
            # Crossover
            if random.random() < self.crossover_rate:
                child = self._crossover(parent1, parent2)
            else:
                child = copy.deepcopy(parent1)
            
            # Mutation
            if random.random() < self.mutation_rate:
                child = self._mutate(child, parameter_space)
            
            new_population.append(child)
        
        return new_population[:self.population_size]
    
    def _tournament_selection(
        self,
        scored_population: List[tuple],
        tournament_size: int = 3
    ) -> Dict[str, Any]:
        """Select individual using tournament selection."""
        tournament = random.sample(scored_population, min(tournament_size, len(scored_population)))
        winner = max(tournament, key=lambda x: x[1])
        return winner[0]
    
    def _crossover(
        self,
        parent1: Dict[str, Any],
        parent2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform crossover between two parents."""
        child = {}
        
        for param_name in parent1.keys():
            # Randomly choose from either parent
            if random.random() < 0.5:
                child[param_name] = parent1[param_name]
            else:
                child[param_name] = parent2[param_name]
        
        return child
    
    def _mutate(
        self,
        individual: Dict[str, Any],
        parameter_space: Dict[str, tuple]
    ) -> Dict[str, Any]:
        """Mutate an individual's parameters."""
        mutated = copy.deepcopy(individual)
        
        # Select random parameter to mutate
        param_to_mutate = random.choice(list(parameter_space.keys()))
        min_val, max_val = parameter_space[param_to_mutate]
        
        # Apply mutation
        if isinstance(min_val, int) and isinstance(max_val, int):
            # For integers, random reset
            mutated[param_to_mutate] = random.randint(min_val, max_val)
        else:
            # For floats, add Gaussian noise
            current_val = mutated[param_to_mutate]
            mutation = random.gauss(0, (max_val - min_val) * 0.1)
            mutated[param_to_mutate] = max(min_val, min(max_val, current_val + mutation))
        
        return mutated
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Get detailed optimization report."""
        if not self.fitness_history:
            return {
                'status': 'not_run',
                'best_fitness': None,
                'best_parameters': None
            }
        
        return {
            'status': 'complete',
            'generations_run': len(self.fitness_history),
            'best_fitness': self.best_fitness,
            'best_parameters': self.best_individual,
            'convergence': self._calculate_convergence(),
            'fitness_improvement': {
                'initial': self.fitness_history[0]['best'],
                'final': self.fitness_history[-1]['best'],
                'improvement': self.fitness_history[-1]['best'] - self.fitness_history[0]['best']
            }
        }
    
    def _calculate_convergence(self) -> float:
        """Calculate convergence metric (0-1, higher is more converged)."""
        if len(self.fitness_history) < 2:
            return 0.0
        
        # Compare recent generations
        recent = 10
        if len(self.fitness_history) < recent:
            recent = len(self.fitness_history)
        
        recent_best = [gen['best'] for gen in self.fitness_history[-recent:]]
        variance = sum((x - self.best_fitness) ** 2 for x in recent_best) / recent
        
        # Lower variance = higher convergence
        convergence = 1.0 / (1.0 + variance)
        return convergence
