# src/strategy/base_strategy.py

from enum import Enum
from typing import Dict, List

class StrategyType(Enum):
    SIMPLE = "simple"
    AGGRESSIVE = "aggressive"
    TIGHT = "tight"
    ALLIN = "allin"
    
    @classmethod
    def list_names(cls) -> List[str]:
        return [strategy.value for strategy in cls]

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