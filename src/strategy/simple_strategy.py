# src/strategy/simple_strategy.py

from typing import Dict
import logging
from sample.slumbot_api import ParseAction
from .base_strategy import BaseStrategy

class SimpleStrategy(BaseStrategy):
    """Simple strategy implementation (always check/call)"""
    
    def decide_action(self, game_state: Dict) -> str:
        """Implements the current sample strategy of always check/call"""
        self.update_game_state(game_state)
        
        action_info = ParseAction(self.current_action)
        
        if 'error' in action_info:
            logging.error(f"Error parsing action: {action_info['error']}")
            return 'f'
            
        # アクティブなベットがある場合はコール、ない場合はチェック
        return 'c' if action_info['last_bettor'] != -1 else 'k'