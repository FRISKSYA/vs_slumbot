# src/strategy/aggressive_strategy.py

from typing import Dict
import logging
from sample.slumbot_api import ParseAction
from .base_strategy import BaseStrategy

class AggressiveStrategy(BaseStrategy):
    """Aggressive strategy implementation"""
    
    def decide_action(self, game_state: Dict) -> str:
        """Implements an aggressive betting strategy"""
        self.update_game_state(game_state)
        
        action_info = ParseAction(self.current_action)
        
        if 'error' in action_info:
            logging.error(f"Error parsing action: {action_info['error']}")
            return 'f'
        
        # ベットの機会があればポットサイズのベット
        if action_info['last_bettor'] == -1:
            return f'b{action_info["total_last_bet_to"] * 2}'
        else:
            return 'c'  # 既存のベットに対してはコール