from typing import Dict
import logging
from sample.slumbot_api import ParseAction
from .base_strategy import BaseStrategy

class TightStrategy(BaseStrategy):
    """Tight strategy implementation"""
    
    def decide_action(self, game_state: Dict) -> str:
        self.update_game_state(game_state)
        
        try:
            action_info = ParseAction(self.current_action)
            
            if 'error' in action_info:
                logging.error(f"Error parsing action: {action_info['error']}")
                return 'f'
            
            return 'k' if action_info['last_bettor'] == -1 else 'f'
        except Exception as e:
            logging.error(f"Error in TightStrategy: {str(e)}")
            return 'f'
