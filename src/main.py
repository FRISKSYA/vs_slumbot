# src/main.py

import argparse
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add the project root directory to Python path to enable imports
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from strategy.base_strategy import StrategyType
from session.session_manager import SessionManager

def create_session_directory():
    """セッションディレクトリの作成"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    session_name = f"session_{timestamp}"
    session_dir = project_root / 'logs' / session_name
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir

def setup_logging(session_dir, verbose=False):
    """ロギングの設定"""
    log_file = session_dir / 'session.log'
    
    logging.basicConfig(
        level=logging.INFO if verbose else logging.WARNING,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return log_file

def main():
    parser = argparse.ArgumentParser(description='Poker Bot vs Slumbot')
    parser.add_argument('--username', type=str, help='Username for Slumbot API')
    parser.add_argument('--password', type=str, help='Password for Slumbot API')
    parser.add_argument('--hands', type=int, default=100,
                        help='Number of hands to play (default: 100)')
    parser.add_argument('--chunk-size', type=int, default=1000,
                        help='Number of hands per chunk (default: 1000)')
    parser.add_argument('--strategy', type=str, default='simple',
                        choices=StrategyType.list_names(),
                        help='Strategy to use for playing (default: simple)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose output')
    
    args = parser.parse_args()
    
    # セッションの準備
    session_dir = create_session_directory()
    setup_logging(session_dir, args.verbose)
    
    logging.info("Starting poker session...")
    logging.info(f"Number of hands to play: {args.hands}")
    logging.info(f"Chunk size: {args.chunk_size}")
    logging.info(f"Using strategy: {args.strategy}")
    
    # セッションの実行
    try:
        session = SessionManager(
            total_hands=args.hands,
            strategy_type=args.strategy,
            chunk_size=args.chunk_size,
            username=args.username,
            password=args.password
        )
        
        analyzer = session.run()
        
        # グラフの作成と保存
        graph_path = analyzer.create_graph(session_dir)
        if graph_path:
            logging.info(f"Session graph saved to: {graph_path}")
            
        logging.info("Session complete.")
        
        # 結果の表示
        if analyzer.winnings_history:
            print(f"\nSession complete - Final results:")
            print(f"Total hands played: {analyzer.hands_played}")
            print(f"Final balance: {analyzer.cumulative_winnings:,} chips")
            print(f"Average per hand: {analyzer.cumulative_winnings/analyzer.hands_played:,.1f}")
            print(f"Session files saved in: {session_dir}")
        
    except KeyboardInterrupt:
        logging.warning("Session interrupted by user.")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())