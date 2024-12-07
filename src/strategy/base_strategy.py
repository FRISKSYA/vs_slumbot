# src/strategy/base_strategy.py

from typing import Dict, List, Optional, Tuple
import logging

class BaseStrategy:
    """Base class for poker playing strategies"""
    
    def __init__(self):
        self.hole_cards: List[str] = []
        self.board: List[str] = []
        self.position: int = 0  # 0 = BB, 1 = SB
        self.current_action: str = ''
        
    def decide_action(self, game_state: Dict) -> str:
        """
        Decides the next action based on the current game state
        Returns: 'f' (fold), 'c' (call), 'k' (check), or 'b' + amount (bet/raise)
        """
        # This should be overridden by concrete strategy classes
        raise NotImplementedError
        
    def update_game_state(self, game_state: Dict) -> None:
        """Updates the internal state with the current game information"""
        self.hole_cards = game_state.get('hole_cards', [])
        self.board = game_state.get('board', [])
        self.position = game_state.get('client_pos', 0)
        self.current_action = game_state.get('action', '')
        
    def parse_current_street(self) -> int:
        """Determines the current street based on the board cards"""
        board_length = len(self.board)
        if board_length == 0:
            return 0  # Preflop
        elif board_length == 3:
            return 1  # Flop
        elif board_length == 4:
            return 2  # Turn
        elif board_length == 5:
            return 3  # River
        else:
            raise ValueError(f"Invalid board length: {board_length}")

class SimpleStrategy(BaseStrategy):
    """Simple strategy implementation (current sample logic)"""
    
    def decide_action(self, game_state: Dict) -> str:
        """Implements the current sample strategy of always check/call"""
        self.update_game_state(game_state)
        
        # Parse the current action string
        from sample.slumbot_api import ParseAction  # Temporary until we refactor this
        action_info = ParseAction(self.current_action)
        
        if 'error' in action_info:
            logging.error(f"Error parsing action: {action_info['error']}")
            return 'f'  # Default to fold in case of error
            
        # Implement the simple "always check/call" strategy
        if action_info['last_bettor'] != -1:
            return 'c'  # Call if there's a bet
        else:
            return 'k'  # Check if no bet
