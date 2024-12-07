# src/main.py

import argparse
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add the project root directory to Python path to enable imports
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from sample.slumbot_api import PlayHand, Login, NewHand, Act  # NewHand, Actを追加
from analysis.session_analyzer import SessionAnalyzer
from strategy.base_strategy import StrategyType 
from strategy.factory import create_strategy 

def create_session_directory():
    """Create a new directory for the current session"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    session_name = f"session_{timestamp}"
    session_dir = project_root / 'logs' / session_name
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir

def setup_logging(session_dir, verbose=False):
    """Set up logging configuration for the session"""
    log_file = session_dir / 'session.log'
    
    # Remove any existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # File handler - always logs everything
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    
    # Console handler - only logs progress updates
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO if verbose else logging.WARNING)
    console_handler.setFormatter(logging.Formatter('%(message)s'))
    
    # Custom filter for progress updates
    class ProgressFilter(logging.Filter):
        def filter(self, record):
            return 'Progress' in record.msg or record.levelno >= logging.WARNING

    console_handler.addFilter(ProgressFilter())
    
    # Configure root logger
    logging.root.setLevel(logging.INFO)
    logging.root.addHandler(file_handler)
    logging.root.addHandler(console_handler)
    
    return log_file

def play_session(num_hands, username=None, password=None, strategy_type='simple'):
    """Play a session of poker hands"""
    analyzer = SessionAnalyzer()
    strategy = create_strategy(strategy_type)
    
    # Initialize session
    token = None
    if username and password:
        logging.info("Logging in with provided credentials...")
        token = Login(username, password)

    hands_completed = 0
    last_progress_report = -1  # 最後に進捗を報告したハンド数
    
    try:
        # Start first hand
        game_state = NewHand(token)
        token = game_state.get('token', token)
        
        while hands_completed < num_hands:
            try:
                # 現在のゲーム状態に基づいてアクションを決定
                action = strategy.decide_action(game_state)
                
                # アクションを実行
                game_state = Act(token, action)
                token = game_state.get('token', token)
                
                # ハンドが終了したかチェック
                if 'winnings' in game_state:
                    winnings = game_state['winnings']
                    analyzer.record_hand(winnings)
                    hands_completed += 1
                    
                    # 進捗の表示（10%単位でのみ表示）
                    current_progress = (hands_completed * 10) // num_hands
                    if current_progress > last_progress_report:
                        progress_percentage = (hands_completed / num_hands) * 100
                        logging.info(f"Progress: {progress_percentage:.1f}% ({hands_completed}/{num_hands} hands)")
                        last_progress_report = current_progress
                    
                    # 次のハンドを開始（ただし最後のハンドの場合は除く）
                    if hands_completed < num_hands:
                        game_state = NewHand(token)
                        token = game_state.get('token', token)
                
            except Exception as e:
                logging.error(f"Error during hand: {str(e)}")
                # エラーが発生した場合は新しいハンドを開始
                game_state = NewHand(token)
                token = game_state.get('token', token)
                continue
                
    except Exception as e:
        logging.error(f"Error occurred during play: {str(e)}")
    finally:
        # 最終進捗の表示（100%に達していない場合）
        if hands_completed == num_hands and last_progress_report != 10:
            logging.info(f"Progress: 100.0% ({num_hands}/{num_hands} hands)")
        
        stats = analyzer.get_statistics()
        if stats:
            logging.info("Session Statistics:")
            for key, value in stats.items():
                logging.info(f"{key}: {value}")
        
        return analyzer

def main():
    parser = argparse.ArgumentParser(description='Poker Bot vs Slumbot')
    parser.add_argument('--username', type=str, help='Username for Slumbot API')
    parser.add_argument('--password', type=str, help='Password for Slumbot API')
    parser.add_argument('--hands', type=int, default=100,
                        help='Number of hands to play (default: 100)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose output')
    parser.add_argument('--strategy', type=str, default='simple',
                        choices=StrategyType.list_names(),  # 利用可能な戦略の一覧
                        help='Strategy to use for playing')
    
    args = parser.parse_args()
    
    # Create session directory and setup logging
    session_dir = create_session_directory()
    setup_logging(session_dir, args.verbose)
    
    logging.info("Starting poker session...")
    logging.info(f"Number of hands to play: {args.hands}")
    logging.info(f"Using strategy: {args.strategy}")
    
    # Play poker session
    try:
        analyzer = play_session(
            args.hands,
            args.username,
            args.password,
            strategy_type=args.strategy
        )
        
        # Create and save graph in session directory
        graph_path = analyzer.create_graph(session_dir)
        if graph_path:
            logging.info(f"Session graph saved to: {graph_path}")
            
        logging.info("Session complete.")
        
        # Print final results to console regardless of verbose mode
        if analyzer.winnings_history:
            print(f"\nSession complete - Final results:")
            print(f"Total hands played: {args.hands}")
            print(f"Final balance: {analyzer.cumulative_winnings:,} chips")
            print(f"Average per hand: {analyzer.cumulative_winnings/args.hands:,.1f}")
            print(f"Session files saved in: {session_dir}")
        
    except KeyboardInterrupt:
        logging.warning("Session interrupted by user.")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())