import argparse
import sys
import logging
from pathlib import Path

# Add the project root directory to Python path to enable imports
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from sample.slumbot_api import PlayHand, Login

def setup_logging():
    """Set up basic logging configuration"""
    log_dir = project_root / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'poker_session.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def play_session(num_hands, username=None, password=None):
    """Play a session of poker hands"""
    # Initialize session
    token = None
    if username and password:
        logging.info("Logging in with provided credentials...")
        token = Login(username, password)
    
    # Play hands
    total_winnings = 0
    hands_played = 0
    
    try:
        for i in range(num_hands):
            logging.info(f"Playing hand {i+1}/{num_hands}")
            token, hand_winnings = PlayHand(token)
            total_winnings += hand_winnings
            hands_played += 1
            logging.info(f"Hand {i+1} completed. Winnings: {hand_winnings}. "
                        f"Total so far: {total_winnings}")
    except Exception as e:
        logging.error(f"Error occurred during play: {str(e)}")
    finally:
        logging.info(f"Session completed. Played {hands_played} hands.")
        logging.info(f"Final total winnings: {total_winnings}")
        return total_winnings

def main():
    parser = argparse.ArgumentParser(description='Poker Bot vs Slumbot')
    parser.add_argument('--username', type=str, help='Username for Slumbot API')
    parser.add_argument('--password', type=str, help='Password for Slumbot API')
    parser.add_argument('--hands', type=int, default=100,
                        help='Number of hands to play (default: 100)')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    logging.info("Starting poker session...")
    
    # Play poker session
    try:
        total_winnings = play_session(args.hands, args.username, args.password)
        logging.info(f"Session complete. Total winnings: {total_winnings}")
    except KeyboardInterrupt:
        logging.info("Session interrupted by user.")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
