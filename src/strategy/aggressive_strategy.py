from typing import Dict
import logging
from sample.slumbot_api import ParseAction
from .base_strategy import BaseStrategy

class AggressiveStrategy(BaseStrategy):
    """Aggressive betting strategy implementation"""
    
    def decide_action(self, game_state: Dict) -> str:
        self.update_game_state(game_state)
        
        try:
            action_info = ParseAction(self.current_action)
            
            if 'error' in action_info:
                logging.error(f"Error parsing action: {action_info['error']}")
                return 'f'
            
            # ベットの機会があれば、ポットサイズのベット
            if action_info['last_bettor'] == -1:
                current_pot = action_info['total_last_bet_to'] * 2
                bet_size = min(current_pot, 20000 - action_info['total_last_bet_to'])
                return f'b{bet_size}'
            else:
                return 'c'
        except Exception as e:
            logging.error(f"Error in AggressiveStrategy: {str(e)}")
            return 'f'
