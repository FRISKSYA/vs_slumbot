# src/strategy/factory.py

from typing import Dict
from .base_strategy import BaseStrategy, StrategyType
from .allin_strategy import AllinStrategy
from .simple_strategy import SimpleStrategy
from .aggressive_strategy import AggressiveStrategy
from .tight_strategy import TightStrategy

def create_strategy(strategy_type: str) -> BaseStrategy:
    """Factory function to create strategy instances"""
    strategies: Dict[str, type] = {
        StrategyType.SIMPLE.value: SimpleStrategy,
        StrategyType.AGGRESSIVE.value: AggressiveStrategy,
        StrategyType.TIGHT.value: TightStrategy,
        StrategyType.ALLIN.value: AllinStrategy
    }
    
    strategy_class = strategies.get(strategy_type)
    if not strategy_class:
        valid_strategies = StrategyType.list_names()
        raise ValueError(f"Invalid strategy type. Choose from: {valid_strategies}")
        
    return strategy_class()