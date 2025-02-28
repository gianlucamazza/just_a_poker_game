"""
Main game module for Just A Poker Game.

This module provides the main game loop and integrates all components.
"""
import logging
import time
from typing import List, Dict, Any, Optional

from just_a_poker_game.engine.card import Card, Deck
from just_a_poker_game.engine.game_state import GameState
from just_a_poker_game.engine.hand_evaluator import HandRank
from just_a_poker_game.player.player import Player, HumanPlayer
from just_a_poker_game.ui.terminal_ui import TerminalUI
from just_a_poker_game.storage.game_storage import GameStorage


logger = logging.getLogger(__name__)


class Game:
    """
    Main game class for poker.
    
    Attributes:
        players (List[Player]): List of players in the game.
        game_state (GameState): Current game state.
        ui (TerminalUI): User interface instance.
        storage (GameStorage): Storage system instance.
        settings (Dict[str, Any]): Game settings.
    """
    
    def __init__(self, players: Optional[List[Player]] = None, settings: Optional[Dict[str, Any]] = None):
        """
        Initialize the poker game.
        
        Args:
            players: List of players (optional).
            settings: Game settings (optional).
        """
        # Default settings
        self.settings: Dict[str, Any] = {
            'starting_chips': 1000,
            'small_blind': 1,
            'big_blind': 2,
            'use_colors': True,
            'animation_speed': 0.5
        }
        
        # Update with provided settings if any
        if settings:
            self.settings.update(settings)
        
        # Initialize storage
        self.storage = GameStorage()
        
        # Initialize UI
        self.ui = TerminalUI(
            use_colors=bool(self.settings['use_colors']),
            animation_speed=float(self.settings['animation_speed'])
        )
        
        # Initialize players
        self.players = players if players else []
        
        # Game state will be initialized when the game starts
        self.game_state: Optional[GameState] = None
    
    def start(self):
        """Start the main game loop."""
        # Initialize game components if needed
        if not self.players:
            existing_players = self.storage.load_players()
            self.players = self.ui.setup_players(existing_players)
        
        # Initialize game state
        self.game_state = GameState(
            self.players, 
            small_blind=int(self.settings['small_blind']), 
            big_blind=int(self.settings['big_blind'])
        )
    
    def play_hand(self):
        """Play a single hand of poker."""
        # Start a new hand
        if not self.game_state:
            return
            
        self.game_state.start_hand()
        
        # Track hand statistics
        for player in self.players:
            player.update_stats(False)  # Increment hands played counter
        
        # Play betting rounds
        hand_complete = False
        while not hand_complete:
            # Display current game state
            if not self.game_state:
                return
                
            self.ui.display_table(self.game_state)
            
            # Get player actions for this betting round
            betting_complete = self._play_betting_round()
            
            # If betting is complete due to all but one player folding, end the hand
            if not self.game_state:
                return
                
            if betting_complete and len(self.game_state.active_players) == 1:
                self._handle_one_player_remaining()
                hand_complete = True
                continue
            
            # Move to next betting round if betting is complete
            if betting_complete:
                if not self.game_state:
                    return
                    
                hand_complete = self.game_state.next_betting_round()
                
                # If we've reached showdown, handle it
                if hand_complete:
                    self._handle_showdown()
    
    def _play_betting_round(self) -> bool:
        """
        Play a betting round.
        
        Returns:
            bool: True if betting round is complete, False otherwise.
        """
        # Continue until betting is complete for this round
        while True:
            # Skip if game state is None
            if not self.game_state:
                return False
                
            # Get current player
            current_player = self.game_state.get_current_player()
            
            # Display current game state with current player highlighted
            self.ui.display_table(self.game_state, current_player)
            
            # Skip if current player is None
            if not current_player:
                return False
                
            # Get player's action
            if isinstance(current_player, HumanPlayer):
                action, amount = self.ui.get_player_action(current_player, self.game_state)
            else:
                # AI player's action
                time.sleep(float(self.settings['animation_speed']))
                action, amount = current_player.get_action(self.game_state)
                
                # Display AI action
                action_desc = f"{action}"
                if action in ['bet', 'raise']:
                    action_desc += f" {amount}"
                print(f"{current_player.name} {action_desc}")
                time.sleep(float(self.settings['animation_speed']))
            
            # Skip if game state is None
            if not self.game_state:
                return False
                
            # Process the action
            betting_complete = self.game_state.player_action(action, amount)
            
            # If betting is complete or only one player remains, end the betting round
            if betting_complete or (self.game_state and len(self.game_state.active_players) == 1):
                return True
    
    def _handle_one_player_remaining(self):
        """Handle the case where only one player remains (all others folded)."""
        if not self.game_state:
            return
            
        # Award pot to the remaining player
        winner = self.game_state.active_players[0]
        pot_amount = self.game_state.pot + sum(p.bet for p in self.game_state.players)
        
        # Collect bets into pot before awarding
        for player in self.game_state.players:
            self.game_state.pot += player.bet
            player.bet = 0
        
        # Award pot
        winner.chips += self.game_state.pot
        
        # Update statistics
        winner.update_stats(True, self.game_state.pot)
        
        # Display result
        self.ui.display_table(self.game_state)
        self.ui.show_game_result([winner], [self.game_state.pot])
        
        # Log results
        logger.info(f"{winner.name} wins {self.game_state.pot} chips (all others folded)")
        
        # Save hand history
        self._record_hand_history([winner], [self.game_state.pot], [])
    
    def _handle_showdown(self):
        """Handle the showdown phase when multiple players remain."""
        if not self.game_state:
            return
            
        # Collect all bets into pot
        for player in self.game_state.players:
            self.game_state.pot += player.bet
            player.bet = 0
        
        # Evaluate hands and determine winners
        results = self.game_state.showdown()
        
        if not results:
            logger.warning("No results from showdown")
            return
            
        winners: List[Player] = []
        amounts: List[int] = []
        hand_results: List = []
        
        if isinstance(results, tuple) and len(results) == 3:
            winners, amounts, hand_results = results
        
        # Award pots
        for winner, amount in zip(winners, amounts):
            winner.chips += amount
            winner.update_stats(True, amount)
        
        # Display results
        self.ui.display_table(self.game_state)
        self.ui.show_game_result(winners, amounts, hand_results)
        
        # Log results
        for winner, amount in zip(winners, amounts):
            logger.info(f"{winner.name} wins {amount} chips at showdown")
        
        # Save hand history
        self._record_hand_history(winners, amounts, hand_results)
    
    def _record_hand_history(self, winners: List[Player], amounts: List[int], hand_results: List):
        """
        Record the hand history for future reference.
        
        Args:
            winners: List of winning players.
            amounts: List of amounts won.
            hand_results: Hand evaluation results.
        """
        if not self.game_state:
            return
            
        # Create history entry
        history: Dict[str, Any] = {
            'winners': [w.name for w in winners],
            'amounts': amounts,
            'players': [p.name for p in self.game_state.players],
            'hands': {},
            'community_cards': [str(c) for c in self.game_state.community_cards],
            'timestamp': time.time()
        }
        
        # Add hand information
        for player in self.game_state.players:
            if player.hand:
                history['hands'][player.name] = [str(c) for c in player.hand]
        
        # Save to storage
        self.storage.save_game_history(history)
    
    def run_game(self):
        """Run the main game loop."""
        self.start()
        running = True
        
        while running:
            choice = self.ui.main_menu()
            
            if choice == "1":  # New Game
                self.start()
                self._play_game()
            
            elif choice == "2":  # Load Game
                self.players = self.storage.load_players()
                if not self.players:
                    print("No saved players found.")
                    continue
                self.start()
                self._play_game()
            
            elif choice == "3":  # Player Statistics
                if not self.players:
                    self.players = self.storage.load_players()
                self.ui.show_game_stats(self.players)
            
            elif choice == "4":  # Settings
                self.settings = self.ui.settings_menu(self.settings)
                # Update UI with new settings
                self.ui = TerminalUI(
                    use_colors=bool(self.settings['use_colors']),
                    animation_speed=float(self.settings['animation_speed'])
                )
                self.storage.save_settings(self.settings)
            
            elif choice == "5":  # Exit
                if self.players:
                    self.storage.save_players(self.players)
                running = False
    
    def _play_game(self):
        """Play a game consisting of multiple hands."""
        playing = True
        
        while playing and len(self.players) >= 2:
            # Check if any players are out of chips
            self.players = [p for p in self.players if p.chips > 0]
            
            if len(self.players) < 2:
                print("Not enough players with chips to continue.")
                break
            
            # Play a hand
            self.play_hand()
            
            # Ask to continue
            choice = input("Play another hand? (y/n): ").strip().lower()
            if choice != 'y':
                playing = False
        
        # Save player data
        if self.players:
            self.storage.save_players(self.players)