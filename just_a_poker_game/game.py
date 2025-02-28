"""
Main game module for Just A Poker Game.

This module provides the main game loop and integrates all components.
"""
import logging
import os
import time
from typing import List, Dict, Any, Optional, Tuple

from just_a_poker_game.engine.game_state import GameState, BettingRound
from just_a_poker_game.player.player import Player, HumanPlayer
from just_a_poker_game.ai.basic_ai import BasicAIPlayer
from just_a_poker_game.ui.terminal_ui import TerminalUI
from just_a_poker_game.storage.game_storage import GameStorage
from just_a_poker_game.engine.hand_evaluator import HandEvaluator


logger = logging.getLogger(__name__)


class PokerGame:
    """
    Main poker game class that orchestrates the game flow.
    
    Attributes:
        players (List[Player]): List of players in the game.
        game_state (GameState): Current game state.
        ui (TerminalUI): User interface instance.
        storage (GameStorage): Storage system instance.
        settings (Dict[str, Any]): Game settings.
    """
    
    def __init__(self, players: List[Player] = None, settings: Dict[str, Any] = None):
        """
        Initialize the poker game.
        
        Args:
            players: List of players (optional).
            settings: Game settings (optional).
        """
        # Initialize settings with defaults
        self.settings = {
            'small_blind': 1,
            'big_blind': 2,
            'starting_chips': 1000,
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
            use_colors=self.settings['use_colors'],
            animation_speed=self.settings['animation_speed']
        )
        
        # Initialize players
        self.players = players if players else []
        
        # Game state will be initialized when the game starts
        self.game_state = None
    
    def setup_game(self):
        """Set up a new game by initializing players and game state."""
        # Set up players if not already done
        if not self.players:
            existing_players = self.storage.load_players()
            self.players = self.ui.setup_players(existing_players)
        
        # Initialize game state
        self.game_state = GameState(
            self.players, 
            small_blind=self.settings['small_blind'], 
            big_blind=self.settings['big_blind']
        )
    
    def play_hand(self):
        """Play a single hand of poker."""
        # Start a new hand
        self.game_state.start_hand()
        
        # Track hand statistics
        for player in self.players:
            player.update_stats(False)  # Increment hands played counter
        
        # Play betting rounds
        hand_complete = False
        while not hand_complete:
            # Display current game state
            self.ui.display_table(self.game_state)
            
            # Get player actions for this betting round
            betting_complete = self._play_betting_round()
            
            # If betting is complete due to all but one player folding, end the hand
            if betting_complete and len(self.game_state.active_players) == 1:
                self._handle_one_player_remaining()
                hand_complete = True
                continue
            
            # Move to next betting round if betting is complete
            if betting_complete:
                hand_complete = self.game_state.next_betting_round()
                
                # If we've reached showdown, handle it
                if hand_complete:
                    self._handle_showdown()
        
        # Save game state after hand
        self._save_game_state()
    
    def _play_betting_round(self) -> bool:
        """
        Play a betting round.
        
        Returns:
            bool: True if betting round is complete, False otherwise.
        """
        # Continue until betting is complete for this round
        while True:
            # Get current player
            current_player = self.game_state.get_current_player()
            
            # Display current game state with current player highlighted
            self.ui.display_table(self.game_state, current_player)
            
            # Get player's action
            if isinstance(current_player, HumanPlayer):
                action, amount = self.ui.get_player_action(current_player, self.game_state)
            else:
                # AI player's action
                time.sleep(self.settings['animation_speed'])
                action, amount = current_player.get_action(self.game_state)
                
                # Display AI action
                action_desc = f"{action}"
                if action in ['bet', 'raise']:
                    action_desc += f" {amount}"
                print(f"{current_player.name} {action_desc}")
                time.sleep(self.settings['animation_speed'])
            
            # Process the action
            betting_complete = self.game_state.player_action(action, amount)
            
            # If betting is complete or only one player remains, end the betting round
            if betting_complete or len(self.game_state.active_players) == 1:
                return True
    
    def _handle_one_player_remaining(self):
        """Handle the case where only one player remains (all others folded)."""
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
        
        # Reset pot
        self.game_state.pot = 0
    
    def _handle_showdown(self):
        """Handle the showdown phase of the game."""
        # Collect final bets into pot
        for player in self.game_state.players:
            self.game_state.pot += player.bet
            player.bet = 0
        
        # Evaluate hands
        hand_results = self.game_state.showdown()
        
        # Display final table state with all cards
        self.ui.display_table(self.game_state)
        
        # Determine winners (players with highest hand rank)
        if hand_results:
            highest_rank = hand_results[0][1].value
            winners = [player for player, rank, _ in hand_results if rank.value == highest_rank]
            
            # Award pot
            pot_per_winner = self.game_state.pot // len(winners)
            remainder = self.game_state.pot % len(winners)
            
            award_amounts = []
            for i, winner in enumerate(winners):
                award = pot_per_winner
                if i < remainder:
                    award += 1
                
                winner.chips += award
                award_amounts.append(award)
                
                # Update statistics
                winner.update_stats(True, award)
            
            # Show results
            self.ui.show_game_result(winners, award_amounts, hand_results)
        else:
            # No one to award pot to (should not happen)
            self.ui.show_game_result([], [])
        
        # Reset pot
        self.game_state.pot = 0
    
    def _save_game_state(self):
        """Save the current game state to storage."""
        # Save player data
        self.storage.save_players(self.players)
        
        # Save game history entry
        history_entry = {
            'timestamp': time.time(),
            'players': [p.name for p in self.players],
            'chips': {p.name: p.chips for p in self.players}
        }
        self.storage.save_game_history(history_entry)
    
    def start_game(self):
        """Start the main game loop."""
        # Set up the game
        self.setup_game()
        
        # Main game loop
        running = True
        while running:
            # Check if any player is out of chips
            active_players = [p for p in self.players if p.chips > 0]
            
            # If only one player has chips, they win
            if len(active_players) == 1:
                winner = active_players[0]
                print(f"{winner.name} wins the game with {winner.chips} chips!")
                input("Press Enter to return to main menu...")
                return
            
            # Play a hand
            self.play_hand()
            
            # Check if user wants to continue
            choice = input("Continue playing? (y/n): ").strip().lower()
            if choice != 'y':
                running = False
    
    def run_main_menu(self):
        """Run the main menu loop."""
        exit_game = False
        
        while not exit_game:
            choice = self.ui.main_menu()
            
            if choice == "1":  # New Game
                # Set up a new game
                existing_players = self.storage.load_players()
                self.players = self.ui.setup_players(existing_players)
                self.start_game()
            
            elif choice == "2":  # Load Game
                # Load saved players
                self.players = self.storage.load_players()
                
                if not self.players:
                    print("No saved game found.")
                    input("Press Enter to continue...")
                    continue
                
                self.start_game()
            
            elif choice == "3":  # Player Statistics
                # Load saved players and show stats
                self.players = self.storage.load_players()
                
                if not self.players:
                    print("No player statistics available.")
                    input("Press Enter to continue...")
                    continue
                
                self.ui.show_game_stats(self.players)
            
            elif choice == "4":  # Settings
                # Load and modify settings
                loaded_settings = self.storage.load_settings()
                if loaded_settings:
                    self.settings.update(loaded_settings)
                
                updated_settings = self.ui.settings_menu(self.settings)
                self.settings = updated_settings
                
                # Update UI with new settings
                self.ui = TerminalUI(
                    use_colors=self.settings['use_colors'],
                    animation_speed=self.settings['animation_speed']
                )
                
                # Save settings
                self.storage.save_settings(self.settings)
            
            elif choice == "5":  # Exit
                exit_game = True
                print("Thanks for playing Just A Poker Game!")
