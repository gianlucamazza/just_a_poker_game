"""
Main entry point for Just A Poker Game.

This module provides the command-line interface to start the game.
"""
import argparse
import logging
import os
import sys

from just_a_poker_game.game import PokerGame
from just_a_poker_game.storage.game_storage import GameStorage


def setup_logging(verbose: bool = False):
    """Set up logging configuration."""
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # Create logs directory if it doesn't exist
    base_dir = os.path.dirname(os.path.dirname(__file__))
    logs_dir = os.path.join(base_dir, 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Set up logging
    log_file = os.path.join(logs_dir, 'poker_game.log')
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout) if verbose else logging.NullHandler()
        ]
    )


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Just A Poker Game - Texas Hold'em Poker")
    
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('--no-color', action='store_true', help='Disable colored output')
    parser.add_argument('--small-blind', type=int, help='Small blind amount')
    parser.add_argument('--big-blind', type=int, help='Big blind amount')
    parser.add_argument('--starting-chips', type=int, help='Starting chips amount')
    
    return parser.parse_args()


def main():
    """Main entry point."""
    # Parse command-line arguments
    args = parse_args()
    
    # Set up logging
    setup_logging(args.verbose)
    
    # Load settings from storage
    storage = GameStorage()
    settings = storage.load_settings()
    
    # Override settings from command-line arguments
    if args.no_color:
        settings['use_colors'] = False
    if args.small_blind:
        settings['small_blind'] = args.small_blind
    if args.big_blind:
        settings['big_blind'] = args.big_blind
    if args.starting_chips:
        settings['starting_chips'] = args.starting_chips
    
    # Create and run the game
    game = PokerGame(settings=settings)
    game.run_main_menu()


if __name__ == "__main__":
    main()
