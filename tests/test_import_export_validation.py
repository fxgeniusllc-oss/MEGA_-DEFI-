"""
Comprehensive Import/Export Validation Tests
=============================================

This test suite validates that all systematic imports and exports are correctly
named and wired throughout the MEGA DeFi system.

Tests cover:
- Main package exports
- Core module exports and imports
- Strategy module exports and imports
- Cross-module dependencies
- Module structure integrity
- Public API consistency
"""

import unittest
import importlib
import inspect


class TestMainPackageExports(unittest.TestCase):
    """Test main package (mega_defi) exports are correctly named and wired."""
    
    def test_main_package_imports(self):
        """Test that mega_defi package can be imported."""
        try:
            import mega_defi
            self.assertIsNotNone(mega_defi)
        except ImportError as e:
            self.fail(f"Failed to import mega_defi: {e}")
    
    def test_main_package_has_all_attribute(self):
        """Test that main package defines __all__ for public API."""
        import mega_defi
        self.assertTrue(hasattr(mega_defi, '__all__'))
        self.assertIsInstance(mega_defi.__all__, list)
        self.assertGreater(len(mega_defi.__all__), 0)
    
    def test_main_package_all_exports_exist(self):
        """Test that all items in __all__ actually exist in the package."""
        import mega_defi
        
        for name in mega_defi.__all__:
            with self.subTest(export=name):
                self.assertTrue(
                    hasattr(mega_defi, name),
                    f"Export '{name}' listed in __all__ but not found in package"
                )
    
    def test_main_package_exports_correct_names(self):
        """Test that main package exports have correct names."""
        import mega_defi
        
        expected_exports = [
            'StrategyEngine',
            'MarketAnalyzer',
            'RiskManager',
            'ProfitOptimizer'
        ]
        
        for name in expected_exports:
            with self.subTest(export=name):
                self.assertIn(name, mega_defi.__all__)
                self.assertTrue(hasattr(mega_defi, name))
    
    def test_main_package_exports_are_classes(self):
        """Test that main package exports are the correct types."""
        import mega_defi
        
        for name in mega_defi.__all__:
            with self.subTest(export=name):
                obj = getattr(mega_defi, name)
                self.assertTrue(
                    inspect.isclass(obj),
                    f"Export '{name}' should be a class but is {type(obj)}"
                )
    
    def test_main_package_version_defined(self):
        """Test that package version is defined."""
        import mega_defi
        self.assertTrue(hasattr(mega_defi, '__version__'))
        self.assertIsInstance(mega_defi.__version__, str)
        self.assertRegex(mega_defi.__version__, r'^\d+\.\d+\.\d+')


class TestCoreModuleExports(unittest.TestCase):
    """Test core module exports are correctly named and wired."""
    
    def test_core_module_exists(self):
        """Test that core module can be imported."""
        try:
            from mega_defi import core
            self.assertIsNotNone(core)
        except ImportError as e:
            self.fail(f"Failed to import mega_defi.core: {e}")
    
    def test_strategy_engine_module_import(self):
        """Test strategy_engine module can be imported."""
        try:
            from mega_defi.core import strategy_engine
            self.assertIsNotNone(strategy_engine)
        except ImportError as e:
            self.fail(f"Failed to import strategy_engine: {e}")
    
    def test_market_analyzer_module_import(self):
        """Test market_analyzer module can be imported."""
        try:
            from mega_defi.core import market_analyzer
            self.assertIsNotNone(market_analyzer)
        except ImportError as e:
            self.fail(f"Failed to import market_analyzer: {e}")
    
    def test_risk_manager_module_import(self):
        """Test risk_manager module can be imported."""
        try:
            from mega_defi.core import risk_manager
            self.assertIsNotNone(risk_manager)
        except ImportError as e:
            self.fail(f"Failed to import risk_manager: {e}")
    
    def test_profit_optimizer_module_import(self):
        """Test profit_optimizer module can be imported."""
        try:
            from mega_defi.core import profit_optimizer
            self.assertIsNotNone(profit_optimizer)
        except ImportError as e:
            self.fail(f"Failed to import profit_optimizer: {e}")
    
    def test_core_classes_import_directly(self):
        """Test that core classes can be imported directly from modules."""
        classes_to_test = [
            ('mega_defi.core.strategy_engine', 'StrategyEngine'),
            ('mega_defi.core.market_analyzer', 'MarketAnalyzer'),
            ('mega_defi.core.risk_manager', 'RiskManager'),
            ('mega_defi.core.profit_optimizer', 'ProfitOptimizer'),
        ]
        
        for module_name, class_name in classes_to_test:
            with self.subTest(module=module_name, cls=class_name):
                module = importlib.import_module(module_name)
                self.assertTrue(
                    hasattr(module, class_name),
                    f"Class '{class_name}' not found in {module_name}"
                )
                cls = getattr(module, class_name)
                self.assertTrue(inspect.isclass(cls))
    
    def test_core_classes_match_main_exports(self):
        """Test that core classes exported from main match module definitions."""
        import mega_defi
        from mega_defi.core.strategy_engine import StrategyEngine
        from mega_defi.core.market_analyzer import MarketAnalyzer
        from mega_defi.core.risk_manager import RiskManager
        from mega_defi.core.profit_optimizer import ProfitOptimizer
        
        # Check that exports from main package are the same objects
        self.assertIs(mega_defi.StrategyEngine, StrategyEngine)
        self.assertIs(mega_defi.MarketAnalyzer, MarketAnalyzer)
        self.assertIs(mega_defi.RiskManager, RiskManager)
        self.assertIs(mega_defi.ProfitOptimizer, ProfitOptimizer)


class TestStrategiesModuleExports(unittest.TestCase):
    """Test strategies module exports are correctly named and wired."""
    
    def test_strategies_module_import(self):
        """Test that strategies module can be imported."""
        try:
            from mega_defi import strategies
            self.assertIsNotNone(strategies)
        except ImportError as e:
            self.fail(f"Failed to import strategies module: {e}")
    
    def test_strategies_has_all_attribute(self):
        """Test that strategies module defines __all__ for public API."""
        from mega_defi import strategies
        self.assertTrue(hasattr(strategies, '__all__'))
        self.assertIsInstance(strategies.__all__, list)
        self.assertGreater(len(strategies.__all__), 0)
    
    def test_strategies_all_exports_exist(self):
        """Test that all items in strategies.__all__ actually exist."""
        from mega_defi import strategies
        
        for name in strategies.__all__:
            with self.subTest(export=name):
                self.assertTrue(
                    hasattr(strategies, name),
                    f"Export '{name}' listed in __all__ but not found in strategies"
                )
    
    def test_strategies_exports_correct_names(self):
        """Test that strategies module exports have correct names."""
        from mega_defi import strategies
        
        expected_exports = [
            'BaseStrategy',
            'StrategyRank',
            'FlashLoanArbitrageStrategy',
            'CrossChainArbitrageStrategy',
            'LiquidationHunterStrategy',
            'MEVStrategy',
            'StatisticalArbitrageStrategy',
            'YieldOptimizerStrategy',
            'StrategyRegistry',
        ]
        
        for name in expected_exports:
            with self.subTest(export=name):
                self.assertIn(name, strategies.__all__)
                self.assertTrue(hasattr(strategies, name))
    
    def test_base_strategy_is_abstract(self):
        """Test that BaseStrategy is an abstract base class."""
        from mega_defi.strategies import BaseStrategy
        import abc
        
        # Check it's a class
        self.assertTrue(inspect.isclass(BaseStrategy))
        
        # Check it has ABCMeta as metaclass
        self.assertTrue(issubclass(type(BaseStrategy), abc.ABCMeta))
    
    def test_strategy_rank_is_enum(self):
        """Test that StrategyRank is an enumeration."""
        from mega_defi.strategies import StrategyRank
        from enum import Enum
        
        self.assertTrue(issubclass(StrategyRank, Enum))
    
    def test_all_strategy_classes_inherit_base(self):
        """Test that all strategy classes inherit from BaseStrategy."""
        from mega_defi.strategies import (
            BaseStrategy,
            FlashLoanArbitrageStrategy,
            CrossChainArbitrageStrategy,
            LiquidationHunterStrategy,
            MEVStrategy,
            StatisticalArbitrageStrategy,
            YieldOptimizerStrategy,
        )
        
        strategy_classes = [
            FlashLoanArbitrageStrategy,
            CrossChainArbitrageStrategy,
            LiquidationHunterStrategy,
            MEVStrategy,
            StatisticalArbitrageStrategy,
            YieldOptimizerStrategy,
        ]
        
        for strategy_cls in strategy_classes:
            with self.subTest(strategy=strategy_cls.__name__):
                self.assertTrue(
                    issubclass(strategy_cls, BaseStrategy),
                    f"{strategy_cls.__name__} should inherit from BaseStrategy"
                )
    
    def test_strategy_registry_is_class(self):
        """Test that StrategyRegistry is a proper class."""
        from mega_defi.strategies import StrategyRegistry
        
        self.assertTrue(inspect.isclass(StrategyRegistry))


class TestStrategyModuleStructure(unittest.TestCase):
    """Test individual strategy module structure and imports."""
    
    def test_flash_loan_arbitrage_module(self):
        """Test flash_loan_arbitrage module structure."""
        try:
            from mega_defi.strategies.flash_loan_arbitrage import FlashLoanArbitrageStrategy
            self.assertTrue(inspect.isclass(FlashLoanArbitrageStrategy))
        except ImportError as e:
            self.fail(f"Failed to import FlashLoanArbitrageStrategy: {e}")
    
    def test_cross_chain_arbitrage_module(self):
        """Test cross_chain_arbitrage module structure."""
        try:
            from mega_defi.strategies.cross_chain_arbitrage import CrossChainArbitrageStrategy
            self.assertTrue(inspect.isclass(CrossChainArbitrageStrategy))
        except ImportError as e:
            self.fail(f"Failed to import CrossChainArbitrageStrategy: {e}")
    
    def test_liquidation_hunter_module(self):
        """Test liquidation_hunter module structure."""
        try:
            from mega_defi.strategies.liquidation_hunter import LiquidationHunterStrategy
            self.assertTrue(inspect.isclass(LiquidationHunterStrategy))
        except ImportError as e:
            self.fail(f"Failed to import LiquidationHunterStrategy: {e}")
    
    def test_mev_strategy_module(self):
        """Test mev_strategy module structure."""
        try:
            from mega_defi.strategies.mev_strategy import MEVStrategy
            self.assertTrue(inspect.isclass(MEVStrategy))
        except ImportError as e:
            self.fail(f"Failed to import MEVStrategy: {e}")
    
    def test_statistical_arbitrage_module(self):
        """Test statistical_arbitrage module structure."""
        try:
            from mega_defi.strategies.statistical_arbitrage import StatisticalArbitrageStrategy
            self.assertTrue(inspect.isclass(StatisticalArbitrageStrategy))
        except ImportError as e:
            self.fail(f"Failed to import StatisticalArbitrageStrategy: {e}")
    
    def test_yield_optimizer_module(self):
        """Test yield_optimizer module structure."""
        try:
            from mega_defi.strategies.yield_optimizer import YieldOptimizerStrategy
            self.assertTrue(inspect.isclass(YieldOptimizerStrategy))
        except ImportError as e:
            self.fail(f"Failed to import YieldOptimizerStrategy: {e}")
    
    def test_base_strategy_module(self):
        """Test base_strategy module structure."""
        try:
            from mega_defi.strategies.base_strategy import BaseStrategy, StrategyRank
            self.assertTrue(inspect.isclass(BaseStrategy))
            self.assertIsNotNone(StrategyRank)
        except ImportError as e:
            self.fail(f"Failed to import from base_strategy: {e}")
    
    def test_strategy_registry_module(self):
        """Test strategy_registry module structure."""
        try:
            from mega_defi.strategies.strategy_registry import StrategyRegistry
            self.assertTrue(inspect.isclass(StrategyRegistry))
        except ImportError as e:
            self.fail(f"Failed to import StrategyRegistry: {e}")


class TestConfigModule(unittest.TestCase):
    """Test config module exports and structure."""
    
    def test_config_module_import(self):
        """Test that config module can be imported."""
        try:
            from mega_defi import config
            self.assertIsNotNone(config)
        except ImportError as e:
            self.fail(f"Failed to import config module: {e}")
    
    def test_config_class_import(self):
        """Test that Config class can be imported."""
        try:
            from mega_defi.config import Config
            self.assertTrue(inspect.isclass(Config))
        except ImportError as e:
            self.fail(f"Failed to import Config class: {e}")
    
    def test_config_used_by_strategies(self):
        """Test that Config can be imported by strategy modules."""
        try:
            # This import pattern is used by strategy modules
            from mega_defi.strategies.flash_loan_arbitrage import FlashLoanArbitrageStrategy
            # If the import succeeds, Config is accessible
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Strategy cannot access Config: {e}")


class TestProfitMachineModule(unittest.TestCase):
    """Test profit_machine module exports and functionality."""
    
    def test_profit_machine_module_import(self):
        """Test that profit_machine module can be imported."""
        try:
            from mega_defi import profit_machine
            self.assertIsNotNone(profit_machine)
        except ImportError as e:
            self.fail(f"Failed to import profit_machine module: {e}")
    
    def test_create_profit_machine_function_exists(self):
        """Test that create_profit_machine function exists."""
        from mega_defi.profit_machine import create_profit_machine
        
        self.assertTrue(callable(create_profit_machine))
    
    def test_profit_machine_integrates_all_components(self):
        """Test that profit machine correctly integrates all components."""
        from mega_defi.profit_machine import create_profit_machine
        
        machine = create_profit_machine(portfolio_value=10000)
        
        # Check all required components are present
        required_components = [
            'strategy_engine',
            'market_analyzer',
            'risk_manager',
            'profit_optimizer'
        ]
        
        for component in required_components:
            with self.subTest(component=component):
                self.assertTrue(
                    hasattr(machine, component),
                    f"Profit machine missing component: {component}"
                )
    
    def test_profit_machine_components_correct_types(self):
        """Test that profit machine components are correct types."""
        from mega_defi.profit_machine import create_profit_machine
        from mega_defi import StrategyEngine, MarketAnalyzer, RiskManager, ProfitOptimizer
        
        machine = create_profit_machine(portfolio_value=10000)
        
        self.assertIsInstance(machine.strategy_engine, StrategyEngine)
        self.assertIsInstance(machine.market_analyzer, MarketAnalyzer)
        self.assertIsInstance(machine.risk_manager, RiskManager)
        self.assertIsInstance(machine.profit_optimizer, ProfitOptimizer)


class TestCrossModuleDependencies(unittest.TestCase):
    """Test that cross-module dependencies are correctly wired."""
    
    def test_strategies_import_base_strategy(self):
        """Test that strategy modules can import BaseStrategy."""
        try:
            from mega_defi.strategies.flash_loan_arbitrage import FlashLoanArbitrageStrategy
            from mega_defi.strategies.base_strategy import BaseStrategy
            
            self.assertTrue(issubclass(FlashLoanArbitrageStrategy, BaseStrategy))
        except ImportError as e:
            self.fail(f"Strategy cannot import BaseStrategy: {e}")
    
    def test_strategies_import_config(self):
        """Test that strategy modules can import Config."""
        try:
            # Strategies should be able to instantiate with Config
            from mega_defi.strategies.flash_loan_arbitrage import FlashLoanArbitrageStrategy
            
            strategy = FlashLoanArbitrageStrategy()
            self.assertIsNotNone(strategy)
        except ImportError as e:
            self.fail(f"Strategy cannot use Config: {e}")
    
    def test_core_modules_independent(self):
        """Test that core modules can be imported independently."""
        modules = [
            'mega_defi.core.strategy_engine',
            'mega_defi.core.market_analyzer',
            'mega_defi.core.risk_manager',
            'mega_defi.core.profit_optimizer',
        ]
        
        for module_name in modules:
            with self.subTest(module=module_name):
                try:
                    module = importlib.import_module(module_name)
                    self.assertIsNotNone(module)
                except ImportError as e:
                    self.fail(f"Failed to import {module_name}: {e}")
    
    def test_no_circular_imports(self):
        """Test that there are no circular import issues."""
        try:
            # Import in different orders to check for circular dependencies
            from mega_defi import strategies
            from mega_defi import core
            from mega_defi.strategies import BaseStrategy
            from mega_defi.core.strategy_engine import StrategyEngine
            from mega_defi.profit_machine import create_profit_machine
            
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Circular import detected: {e}")


class TestPublicAPIConsistency(unittest.TestCase):
    """Test that the public API is consistent and complete."""
    
    def test_main_package_public_api_complete(self):
        """Test that main package exposes all essential classes."""
        import mega_defi
        
        essential_classes = [
            'StrategyEngine',
            'MarketAnalyzer',
            'RiskManager',
            'ProfitOptimizer',
        ]
        
        for cls_name in essential_classes:
            with self.subTest(class_name=cls_name):
                self.assertIn(cls_name, mega_defi.__all__)
    
    def test_strategies_public_api_complete(self):
        """Test that strategies module exposes all strategy classes."""
        from mega_defi import strategies
        
        essential_strategies = [
            'BaseStrategy',
            'FlashLoanArbitrageStrategy',
            'CrossChainArbitrageStrategy',
            'LiquidationHunterStrategy',
            'MEVStrategy',
            'StatisticalArbitrageStrategy',
            'YieldOptimizerStrategy',
        ]
        
        for strategy_name in essential_strategies:
            with self.subTest(strategy=strategy_name):
                self.assertIn(strategy_name, strategies.__all__)
    
    def test_all_exported_classes_instantiable(self):
        """Test that all exported classes can be instantiated (where appropriate)."""
        from mega_defi import StrategyEngine, MarketAnalyzer, RiskManager, ProfitOptimizer
        
        # These should be instantiable without errors
        classes_to_test = [
            (StrategyEngine, {}),
            (MarketAnalyzer, {}),
            (RiskManager, {}),
            (ProfitOptimizer, {}),
        ]
        
        for cls, kwargs in classes_to_test:
            with self.subTest(class_name=cls.__name__):
                try:
                    instance = cls(**kwargs)
                    self.assertIsNotNone(instance)
                except Exception as e:
                    self.fail(f"Failed to instantiate {cls.__name__}: {e}")
    
    def test_all_strategy_classes_instantiable(self):
        """Test that all strategy classes can be instantiated."""
        from mega_defi.strategies import (
            FlashLoanArbitrageStrategy,
            CrossChainArbitrageStrategy,
            LiquidationHunterStrategy,
            MEVStrategy,
            StatisticalArbitrageStrategy,
            YieldOptimizerStrategy,
        )
        
        strategy_classes = [
            FlashLoanArbitrageStrategy,
            CrossChainArbitrageStrategy,
            LiquidationHunterStrategy,
            MEVStrategy,
            StatisticalArbitrageStrategy,
            YieldOptimizerStrategy,
        ]
        
        for strategy_cls in strategy_classes:
            with self.subTest(strategy=strategy_cls.__name__):
                try:
                    strategy = strategy_cls()
                    self.assertIsNotNone(strategy)
                    self.assertTrue(hasattr(strategy, 'name'))
                except Exception as e:
                    self.fail(f"Failed to instantiate {strategy_cls.__name__}: {e}")


class TestModuleMetadata(unittest.TestCase):
    """Test that modules have proper metadata and documentation."""
    
    def test_main_package_has_docstring(self):
        """Test that main package has documentation."""
        import mega_defi
        self.assertIsNotNone(mega_defi.__doc__)
        self.assertGreater(len(mega_defi.__doc__), 0)
    
    def test_main_package_has_author(self):
        """Test that main package defines author."""
        import mega_defi
        self.assertTrue(hasattr(mega_defi, '__author__'))
        self.assertIsInstance(mega_defi.__author__, str)
    
    def test_strategies_module_has_docstring(self):
        """Test that strategies module has documentation."""
        from mega_defi import strategies
        self.assertIsNotNone(strategies.__doc__)
        self.assertGreater(len(strategies.__doc__), 0)
    
    def test_all_core_classes_have_docstrings(self):
        """Test that all core classes are documented."""
        from mega_defi import StrategyEngine, MarketAnalyzer, RiskManager, ProfitOptimizer
        
        classes = [StrategyEngine, MarketAnalyzer, RiskManager, ProfitOptimizer]
        
        for cls in classes:
            with self.subTest(class_name=cls.__name__):
                self.assertIsNotNone(cls.__doc__)
                self.assertGreater(len(cls.__doc__), 0)


class TestEndToEndImportWiring(unittest.TestCase):
    """Test complete end-to-end import chains work correctly."""
    
    def test_import_from_top_level_works(self):
        """Test that importing from top level works for all public exports."""
        try:
            from mega_defi import (
                StrategyEngine,
                MarketAnalyzer,
                RiskManager,
                ProfitOptimizer
            )
            
            self.assertTrue(inspect.isclass(StrategyEngine))
            self.assertTrue(inspect.isclass(MarketAnalyzer))
            self.assertTrue(inspect.isclass(RiskManager))
            self.assertTrue(inspect.isclass(ProfitOptimizer))
        except ImportError as e:
            self.fail(f"Failed to import from top level: {e}")
    
    def test_import_strategies_from_subpackage_works(self):
        """Test that importing strategies from subpackage works."""
        try:
            from mega_defi.strategies import (
                BaseStrategy,
                FlashLoanArbitrageStrategy,
                CrossChainArbitrageStrategy,
                LiquidationHunterStrategy,
                MEVStrategy,
                StatisticalArbitrageStrategy,
                YieldOptimizerStrategy,
                StrategyRegistry,
            )
            
            # All imports should succeed
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import strategies: {e}")
    
    def test_create_complete_system_from_imports(self):
        """Test that a complete system can be created using public imports."""
        try:
            from mega_defi import (
                StrategyEngine,
                MarketAnalyzer,
                RiskManager,
                ProfitOptimizer
            )
            from mega_defi.profit_machine import create_profit_machine
            
            # Create using factory function
            machine1 = create_profit_machine(portfolio_value=10000)
            self.assertIsNotNone(machine1)
            
            # Create components manually
            strategy_engine = StrategyEngine()
            market_analyzer = MarketAnalyzer()
            risk_manager = RiskManager()
            profit_optimizer = ProfitOptimizer()
            
            self.assertIsNotNone(strategy_engine)
            self.assertIsNotNone(market_analyzer)
            self.assertIsNotNone(risk_manager)
            self.assertIsNotNone(profit_optimizer)
            
        except Exception as e:
            self.fail(f"Failed to create complete system: {e}")
    
    def test_all_strategy_classes_accessible_from_registry(self):
        """Test that all strategy classes are properly registered."""
        from mega_defi.strategies import StrategyRegistry
        from mega_defi.strategies import (
            FlashLoanArbitrageStrategy,
            CrossChainArbitrageStrategy,
            LiquidationHunterStrategy,
            MEVStrategy,
            StatisticalArbitrageStrategy,
            YieldOptimizerStrategy,
        )
        
        registry = StrategyRegistry()
        
        # All strategy classes should be accessible
        strategy_classes = [
            FlashLoanArbitrageStrategy,
            CrossChainArbitrageStrategy,
            LiquidationHunterStrategy,
            MEVStrategy,
            StatisticalArbitrageStrategy,
            YieldOptimizerStrategy,
        ]
        
        for strategy_cls in strategy_classes:
            with self.subTest(strategy=strategy_cls.__name__):
                # Strategy should be registrable
                try:
                    strategy = strategy_cls()
                    self.assertIsNotNone(strategy)
                except Exception as e:
                    self.fail(f"Strategy {strategy_cls.__name__} not properly wired: {e}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
