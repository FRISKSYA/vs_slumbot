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

def create_session_directory():
    """Create a new directory for the current session"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    session_name = f"session_{timestamp}"
    session_dir = project_root / 'logs' / session_name
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir

def setup_logging(session_dir):
    """Set up logging configuration for the session"""
    log_file = session_dir / 'session.log'
    
    # Remove any existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logging.info(f"Session directory created at: {session_dir}")
    logging.info(f"Log file: {log_file}")
    
    return log_file

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
    
    # Create session directory and setup logging
    session_dir = create_session_directory()
    setup_logging(session_dir)
    
    logging.info("Starting poker session...")
    logging.info(f"Number of hands to play: {args.hands}")
    
    # Play poker session
    try:
        analyzer = play_session(args.hands, args.username, args.password)
        
        # Create and save graph in session directory
        graph_path = analyzer.create_graph(session_dir)
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