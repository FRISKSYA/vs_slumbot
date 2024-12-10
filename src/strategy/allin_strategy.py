# src/strategy/allin_strategy.py

from typing import Dict
import logging
from sample.slumbot_api import ParseAction
from .base_strategy import BaseStrategy

class AllinStrategy(BaseStrategy):
    """Strategy that goes all-in on every opportunity"""
    
    def __init__(self):
        super().__init__()
        self.stack_size = 20000  # スタックサイズ
        
    def decide_action(self, game_state: Dict) -> str:
        """常にオールインを選択する戦略
        ただし、APIの制約に従って適切なサイズを計算する
        """
        self.update_game_state(game_state)
        
        try:
            action_info = ParseAction(self.current_action)
            
            if 'error' in action_info:
                logging.error(f"Error parsing action: {action_info['error']}")
                return 'f'
            
            # 既存のベットがある場合
            if action_info['last_bettor'] != -1:
                if action_info['total_last_bet_to'] == self.stack_size:
                    # 既にオールインされている場合はコール
                    return 'c'
                else:
                    # オールインレイズ
                    # 残りスタックを計算（現在のストリートのベット額を考慮）
                    remaining = self.stack_size - action_info['total_last_bet_to']
                    raise_to = action_info['street_last_bet_to'] + remaining
                    return f'b{raise_to}'
            
            # ベットの機会がある場合
            else:
                # 現在のストリートでの有効なベット額を計算
                # street_last_bet_toは現在のストリートでの既存のベット額
                remaining = self.stack_size - action_info['total_last_bet_to']
                return f'b{remaining}'
            
        except Exception as e:
            logging.error(f"Error in AllinStrategy: {str(e)}")
            return 'f'  # エラーの場合はフォールド

    def __str__(self) -> str:
        return "All-in Strategy"