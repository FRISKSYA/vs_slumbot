# src/main.py

import argparse
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add the project root directory to Python path to enable imports
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from sample.slumbot_api import PlayHand, Login
from analysis.session_analyzer import SessionAnalyzer

def setup_logging():
    """Set up basic logging configuration"""
    log_dir = project_root / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f'poker_session_{timestamp}.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return log_dir

def play_session(num_hands, username=None, password=None):
    """Play a session of poker hands"""
    analyzer = SessionAnalyzer()
    
    # Initialize session
    token = None
    if username and password:
        logging.info("Logging in with provided credentials...")
        token = Login(username, password)
    
    # Play hands
    try:
        for i in range(num_hands):
            logging.info(f"Playing hand {i+1}/{num_hands}")
            token, hand_winnings = PlayHand(token)
            analyzer.record_hand(hand_winnings)
            logging.info(f"Hand {i+1} completed. Winnings: {hand_winnings}. "
                        f"Total so far: {analyzer.cumulative_winnings}")
    except Exception as e:
        logging.error(f"Error occurred during play: {str(e)}")
    finally:
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
    
    args = parser.parse_args()
    
    # Setup logging
    log_dir = setup_logging()
    logging.info("Starting poker session...")
    
    # Play poker session
    try:
        analyzer = play_session(args.hands, args.username, args.password)
        
        # Create and save graph
        graph_path = analyzer.create_graph(log_dir)
        if graph_path:
            logging.info(f"Session graph saved to: {graph_path}")
            
        logging.info("Session complete.")
    except KeyboardInterrupt:
        logging.info("Session interrupted by user.")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
