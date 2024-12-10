# src/session/session_manager.py

import time
import logging
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta

from sample.slumbot_api import NewHand, Act
from analysis.session_analyzer import SessionAnalyzer
from strategy.factory import create_strategy
from utils.session_utils import execute_with_retry, with_valid_token

class SessionManager:
    """ポーカーセッションの管理クラス"""
    
    def __init__(
        self,
        total_hands: int,
        strategy_type: str = 'simple',
        chunk_size: int = 1000,
        username: Optional[str] = None,
        password: Optional[str] = None
    ):
        """
        Parameters:
        -----------
        total_hands : int
            プレイする総ハンド数
        strategy_type : str
            使用する戦略タイプ
        chunk_size : int
            一度に実行するハンド数
        username : Optional[str]
            APIユーザー名（オプション）
        password : Optional[str]
            APIパスワード（オプション）
        """
        self.total_hands = total_hands
        self.chunk_size = min(chunk_size, total_hands)
        self.strategy_type = strategy_type
        self.username = username
        self.password = password
        self.analyzer = SessionAnalyzer()
        self.strategy = create_strategy(strategy_type)
        
    def _play_chunk(
        self,
        chunk_size: int,
        token: Optional[str] = None
    ) -> Tuple[SessionAnalyzer, Optional[str]]:
        """
        指定されたサイズのチャンクをプレイ

        Parameters:
        -----------
        chunk_size : int
            このチャンクでプレイするハンド数
        token : Optional[str]
            現在のAPIトークン

        Returns:
        --------
        Tuple[SessionAnalyzer, Optional[str]]
            (チャンクの分析結果, 更新されたトークン)
        """
        chunk_analyzer = SessionAnalyzer()
        current_token = token
        hands_played = 0
        
        try:
            def execute_hand():
                nonlocal current_token, hands_played
                result = play_single_hand(
                    strategy=self.strategy,
                    current_token=current_token,
                    username=self.username,
                    password=self.password
                )
                current_token = result['token']
                if 'winnings' in result:
                    chunk_analyzer.record_hand(result['winnings'])
                    hands_played += 1
                return result
            
            while hands_played < chunk_size:
                execute_with_retry(
                    execute_hand,
                    max_retries=3,
                    delay=1.0,
                    exponential_backoff=True
                )
                
        except Exception as e:
            logging.error(f"Error in chunk: {str(e)}")
            if hands_played == 0:
                raise  # チャンク内で1ハンドも成功していない場合は例外を再送出
            
        return chunk_analyzer, current_token

    def run(self) -> SessionAnalyzer:
        """
        セッション全体を実行

        Returns:
        --------
        SessionAnalyzer
            セッション全体の分析結果
        """
        start_time = datetime.now()
        chunks = (self.total_hands + self.chunk_size - 1) // self.chunk_size
        token = None
        completed_chunks = 0
        
        try:
            for chunk in range(chunks):
                hands_in_chunk = min(
                    self.chunk_size,
                    self.total_hands - chunk * self.chunk_size
                )
                
                logging.info(
                    f"Starting chunk {chunk + 1}/{chunks} "
                    f"({hands_in_chunk} hands)"
                )
                
                try:
                    chunk_analyzer, token = self._play_chunk(hands_in_chunk, token)
                    self.analyzer.merge_results(chunk_analyzer)
                    completed_chunks += 1
                    
                    # 進捗とパフォーマンスの報告
                    self._report_progress(chunk + 1, chunks, start_time)
                    
                    # チャンク間で待機（最後のチャンク以外）
                    if chunk < chunks - 1:
                        time.sleep(1)
                        
                except Exception as e:
                    logging.error(f"Failed to complete chunk {chunk + 1}: {str(e)}")
                    break
                    
        except KeyboardInterrupt:
            logging.warning("Session interrupted by user.")
        finally:
            duration = datetime.now() - start_time
            self._report_final_results(completed_chunks, chunks, duration)
            
        return self.analyzer

    def _report_progress(self, current_chunk: int, total_chunks: int, start_time: datetime) -> None:
        """進捗状況とパフォーマンス指標を報告"""
        elapsed = datetime.now() - start_time
        hands_per_second = self.analyzer.hands_played / elapsed.total_seconds()
        progress = (current_chunk / total_chunks) * 100
        
        logging.info(
            f"Progress: {progress:.1f}% ({current_chunk}/{total_chunks} chunks), "
            f"Hands/sec: {hands_per_second:.1f}, "
            f"Elapsed: {elapsed}"
        )

    def _report_final_results(self, completed_chunks: int, total_chunks: int, duration: timedelta) -> None:
        """セッションの最終結果を報告"""
        hands_per_second = self.analyzer.hands_played / duration.total_seconds()
        completion_rate = (completed_chunks / total_chunks) * 100
        
        logging.info(
            f"\nSession Summary:\n"
            f"Completed chunks: {completed_chunks}/{total_chunks} ({completion_rate:.1f}%)\n"
            f"Hands played: {self.analyzer.hands_played}/{self.total_hands}\n"
            f"Total duration: {duration}\n"
            f"Performance: {hands_per_second:.1f} hands/sec\n"
            f"Final balance: {self.analyzer.cumulative_winnings:,} chips\n"
            f"Average per hand: {self.analyzer.cumulative_winnings/self.analyzer.hands_played:,.1f}"
        )

@with_valid_token
def play_single_hand(
    strategy: Any,
    current_token: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None
) -> Dict[str, Any]:
    """
    単一ハンドをプレイ

    Parameters:
    -----------
    strategy : Any
        使用する戦略オブジェクト
    current_token : Optional[str]
        現在のAPIトークン
    username : Optional[str]
        APIユーザー名（オプション）
    password : Optional[str]
        APIパスワード（オプション）

    Returns:
    --------
    Dict[str, Any]
        ゲーム状態の辞書
    """
    game_state = NewHand(current_token)
    token = game_state.get('token', current_token)
    
    while 'winnings' not in game_state:
        action = strategy.decide_action(game_state)
        game_state = Act(token, action)
        token = game_state.get('token', token)
        
    game_state['token'] = token
    return game_state