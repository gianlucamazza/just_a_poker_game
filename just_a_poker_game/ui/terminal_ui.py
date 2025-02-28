"""
Terminal-based UI for poker game.

This module provides a text-based interface for playing poker
in a terminal environment.
"""
import os
import sys
from typing import List, Dict, Any, Optional, Tuple
import logging

from just_a_poker_game.engine.card import Card
from just_a_poker_game.engine.game_state import GameState, BettingRound
from just_a_poker_game.engine.hand_evaluator import HandRank
from just_a_poker_game.player.player import Player, HumanPlayer


logger = logging.getLogger(__name__)


class TerminalUI:
    """
    Terminal-based UI for poker game.
    
    Provides methods to display game state and get player input.
    """
    
    # ANSI color codes for terminal output
    COLORS = {
        'reset': '\033[0m',
        'bold': '\033[1m',
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'hearts': '\033[31m',    # Red for hearts
        'diamonds': '\033[31m',  # Red for diamonds
        'clubs': '\033[37m',     # White for clubs
        'spades': '\033[34m'     # Blue for spades
    }
    
    def __init__(self, use_colors: bool = True, animation_speed: float = 0.5):
        """
        Initialize the terminal UI.
        
        Args:
            use_colors: Whether to use colored output.
            animation_speed: Delay between animations (seconds).
        """
        self.use_colors = use_colors
        self.animation_speed = animation_speed
        
        # Disable colors if not supported
        if not self._supports_color():
            self.use_colors = False
    
    def _supports_color(self) -> bool:
        """Check if the terminal supports color output."""
        plat = sys.platform
        supported_platform = plat != 'win32' or 'ANSICON' in os.environ
        is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
        return supported_platform and is_a_tty
    
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _color(self, text: str, color: str) -> str:
        """
        Apply color to text if colors are enabled.
        
        Args:
            text: Text to color.
            color: Color to apply.
            
        Returns:
            Colored text string.
        """
        if not self.use_colors:
            return text
        
        color_code = self.COLORS.get(color.lower(), '')
        if not color_code:
            return text
        
        return f"{color_code}{text}{self.COLORS['reset']}"
    
    def format_card(self, card: Card) -> str:
        """
        Format a card for display.
        
        Args:
            card: Card to format.
            
        Returns:
            Formatted card string.
        """
        suit_color = card.suit.name.lower()
        return self._color(f"{card}", suit_color)
    
    def display_table(self, game_state: GameState, current_player: Optional[Player] = None):
        """
        Display the current game state.
        
        Args:
            game_state: Current game state.
            current_player: The player whose turn it is.
        """
        self.clear_screen()
        print(self._color("=== JUST A POKER GAME ===", "bold"))
        print()
        
        # Display pot and current bet
        print(f"Pot: {self._color(str(game_state.pot), 'green')} chips")
        if game_state.current_bet > 0:
            print(f"Current bet: {self._color(str(game_state.current_bet), 'yellow')} chips")
        
        # Display betting round
        round_names = {
            BettingRound.PREFLOP: "Pre-flop",
            BettingRound.FLOP: "Flop",
            BettingRound.TURN: "Turn",
            BettingRound.RIVER: "River",
            BettingRound.SHOWDOWN: "Showdown"
        }
        round_name = round_names.get(game_state.betting_round, "Unknown")
        print(f"Round: {self._color(round_name, 'cyan')}")
        print()
        
        # Display community cards
        print("Community cards:", end=" ")
        if not game_state.community_cards:
            print(self._color("None", "yellow"))
        else:
            for card in game_state.community_cards:
                print(self.format_card(card), end=" ")
            print()
        print()
        
        # Display players
        dealer_pos = game_state.dealer_position
        print("Players:")
        for i, player in enumerate(game_state.players):
            # Format player information
            position = ""
            if i == dealer_pos:
                position = self._color("[D]", "cyan")  # Dealer
            elif i == (dealer_pos + 1) % len(game_state.players) and len(game_state.players) > 2:
                position = self._color("[SB]", "magenta")  # Small blind
            elif i == (dealer_pos + 2) % len(game_state.players) or (i == (dealer_pos + 1) % len(game_state.players) and len(game_state.players) == 2):
                position = self._color("[BB]", "magenta")  # Big blind
            
            # Status indicators
            status = ""
            if player.folded:
                status = self._color("(folded)", "red")
            elif player.chips == 0 and player in game_state.active_players:
                status = self._color("(all-in)", "yellow")
            
            # Current player indicator
            current = " "
            if current_player and player == current_player:
                current = self._color(">", "green")
            
            # Player info line
            player_line = f"{current} {player.name} {position}: {player.chips} chips"
            
            # Add bet info if there's an active bet
            if player.bet > 0:
                player_line += f" (bet: {player.bet})"
            
            # Add status
            if status:
                player_line += f" {status}"
            
            print(player_line)
            
            # Show cards for human players or in showdown
            if (isinstance(player, HumanPlayer) and not player.folded) or game_state.betting_round == BettingRound.SHOWDOWN:
                if player.hand:
                    print(f"   Cards: {self.format_card(player.hand[0])} {self.format_card(player.hand[1])}")
        
        print()
    
    def get_player_action(self, player: Player, game_state: GameState) -> Tuple[str, int]:
        """
        Get action from a human player.
        
        Args:
            player: The player making the decision.
            game_state: Current game state.
            
        Returns:
            Tuple of (action_type, amount)
        """
        print(f"{self._color(player.name, 'bold')}'s turn")
        print(f"Your cards: {self.format_card(player.hand[0])} {self.format_card(player.hand[1])}")
        
        can_check = game_state.current_bet <= player.bet
        call_amount = game_state.current_bet - player.bet
        
        # Show available actions
        print("Available actions:")
        print("  (F)old")
        
        if can_check:
            print("  (C)heck")
        else:
            print(f"  (C)all - {call_amount} chips")
        
        if game_state.current_bet == 0:
            print("  (B)et")
        else:
            print("  (R)aise")
        
        print("  (A)ll-in")
        
        while True:
            choice = input("Your action: ").strip().upper()
            
            if choice == 'F':
                return 'fold', 0
            
            elif choice == 'C':
                if can_check:
                    return 'check', 0
                else:
                    return 'call', 0
            
            elif choice == 'B' and game_state.current_bet == 0:
                while True:
                    try:
                        amount = int(input(f"Bet amount (min {game_state.big_blind}, max {player.chips}): "))
                        if amount < game_state.big_blind:
                            print(f"Minimum bet is {game_state.big_blind}")
                        elif amount > player.chips:
                            print(f"You only have {player.chips} chips")
                        else:
                            return 'bet', amount
                    except ValueError:
                        print("Please enter a valid number")
            
            elif choice == 'R' and game_state.current_bet > 0:
                min_raise = game_state.current_bet + game_state.min_raise
                max_raise = player.chips + player.bet
                
                if min_raise > max_raise:
                    print("You don't have enough chips to raise. Consider calling or going all-in.")
                    continue
                
                while True:
                    try:
                        amount = int(input(f"Raise to (min {min_raise}, max {max_raise}): "))
                        if amount < min_raise:
                            print(f"Minimum raise is to {min_raise}")
                        elif amount > max_raise:
                            print(f"You can raise at most to {max_raise}")
                        else:
                            return 'raise', amount
                    except ValueError:
                        print("Please enter a valid number")
            
            elif choice == 'A':
                return 'all-in', 0
            
            print("Invalid choice, try again")
    
    def show_game_result(self, winners: List[Player], amounts: List[int], hand_results: Optional[List[Tuple[Player, HandRank, List[Card]]]] = None):
        """
        Display the results of a hand.
        
        Args:
            winners: List of winning players.
            amounts: List of amounts won by each player.
            hand_results: List of hand evaluation results (optional).
        """
        print()
        print(self._color("=== HAND RESULTS ===", "bold"))
        
        if not winners:
            print("No winners!")
            return
        
        # Show winners
        for i, (winner, amount) in enumerate(zip(winners, amounts)):
            print(f"{winner.name} wins {self._color(str(amount), 'green')} chips")
        
        # Show hand rankings if available
        if hand_results:
            print()
            print("Hand rankings:")
            
            # Sort by hand rank (highest first)
            hand_results.sort(key=lambda x: x[1].value, reverse=True)
            
            for player, hand_rank, best_cards in hand_results:
                status = "folded" if player.folded else hand_rank.name.replace('_', ' ').title()
                cards_str = " ".join(self.format_card(card) for card in best_cards) if not player.folded else ""
                
                winner_indicator = ""
                if player in winners:
                    winner_indicator = self._color(" (WINNER)", "green")
                
                print(f"{player.name}: {self._color(status, 'cyan')}{winner_indicator}")
                if cards_str:
                    print(f"  {cards_str}")
        
        print()
        input("Press Enter to continue...")
    
    def show_game_stats(self, players: List[Player]):
        """
        Display game statistics.
        
        Args:
            players: List of players.
        """
        self.clear_screen()
        print(self._color("=== PLAYER STATISTICS ===", "bold"))
        print()
        
        # Sort players by chip count (highest first)
        sorted_players = sorted(players, key=lambda p: p.chips, reverse=True)
        
        for player in sorted_players:
            print(f"{self._color(player.name, 'bold')}:")
            print(f"  Chips: {self._color(str(player.chips), 'green')}")
            
            if player.total_hands_played > 0:
                win_rate = (player.hands_won / player.total_hands_played) * 100
                print(f"  Hands played: {player.total_hands_played}")
                print(f"  Hands won: {player.hands_won} ({win_rate:.1f}%)")
                print(f"  Biggest pot won: {player.biggest_pot_won}")
            else:
                print("  No hands played yet")
            print()
        
        input("Press Enter to continue...")
    
    def main_menu(self) -> str:
        """
        Display the main menu and get user choice.
        
        Returns:
            User's menu choice.
        """
        self.clear_screen()
        print(self._color("=== JUST A POKER GAME ===", "bold"))
        print()
        print("Main Menu:")
        print("1. New Game")
        print("2. Load Game")
        print("3. Player Statistics")
        print("4. Settings")
        print("5. Exit")
        print()
        
        while True:
            choice = input("Enter your choice (1-5): ").strip()
            if choice in ["1", "2", "3", "4", "5"]:
                return choice
            print("Invalid choice, try again")
    
    def settings_menu(self, current_settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Display settings menu and get user choices.
        
        Args:
            current_settings: Current game settings.
            
        Returns:
            Updated settings.
        """
        settings = current_settings.copy()
        
        while True:
            self.clear_screen()
            print(self._color("=== GAME SETTINGS ===", "bold"))
            print()
            
            # Display current settings
            print(f"1. Starting Chips: {settings.get('starting_chips', 1000)}")
            print(f"2. Small Blind: {settings.get('small_blind', 1)}")
            print(f"3. Big Blind: {settings.get('big_blind', 2)}")
            print(f"4. Use Colors: {'Yes' if settings.get('use_colors', True) else 'No'}")
            print(f"5. Animation Speed: {settings.get('animation_speed', 0.5)} seconds")
            print("6. Save and Return")
            print()
            
            choice = input("Enter your choice (1-6): ").strip()
            
            if choice == "1":
                try:
                    chips = int(input("Enter starting chips (100-10000): "))
                    if 100 <= chips <= 10000:
                        settings['starting_chips'] = chips
                    else:
                        print("Value must be between 100 and 10000")
                        input("Press Enter to continue...")
                except ValueError:
                    print("Please enter a valid number")
                    input("Press Enter to continue...")
            
            elif choice == "2":
                try:
                    small_blind = int(input("Enter small blind: "))
                    if small_blind > 0:
                        settings['small_blind'] = small_blind
                    else:
                        print("Value must be positive")
                        input("Press Enter to continue...")
                except ValueError:
                    print("Please enter a valid number")
                    input("Press Enter to continue...")
            
            elif choice == "3":
                try:
                    big_blind = int(input("Enter big blind: "))
                    if big_blind > settings.get('small_blind', 1):
                        settings['big_blind'] = big_blind
                    else:
                        print("Big blind must be larger than small blind")
                        input("Press Enter to continue...")
                except ValueError:
                    print("Please enter a valid number")
                    input("Press Enter to continue...")
            
            elif choice == "4":
                use_colors = input("Use colors? (y/n): ").strip().lower()
                settings['use_colors'] = (use_colors == 'y')
            
            elif choice == "5":
                try:
                    speed = float(input("Enter animation speed (0.0-2.0 seconds): "))
                    if 0.0 <= speed <= 2.0:
                        settings['animation_speed'] = speed
                    else:
                        print("Value must be between 0.0 and 2.0")
                        input("Press Enter to continue...")
                except ValueError:
                    print("Please enter a valid number")
                    input("Press Enter to continue...")
            
            elif choice == "6":
                return settings
    
    def setup_players(self, existing_players: Optional[List[Player]] = None) -> List[Player]:
        """
        Set up players for a new game.
        
        Args:
            existing_players: List of existing players, if any.
            
        Returns:
            List of players for the game.
        """
        self.clear_screen()
        print(self._color("=== PLAYER SETUP ===", "bold"))
        print()
        
        players = []
        if existing_players:
            print("Existing players:")
            for i, player in enumerate(existing_players):
                print(f"{i+1}. {player.name} ({player.chips} chips)")
            print()
            
            include = input("Include existing players? (y/n): ").strip().lower()
            if include == 'y':
                players = existing_players.copy()
        
        # Setup new players
        print()
        print("Add players:")
        print("(Enter blank name when done)")
        
        starting_chips = 1000  # Default
        
        player_count = len(players)
        while player_count < 8:  # Maximum 8 players
            name = input(f"Player {player_count+1} name (human): ").strip()
            if not name:
                break
            
            players.append(HumanPlayer(name, starting_chips))
            player_count += 1
        
        # Add AI players
        while player_count < 8:
            ai_name = input(f"AI Player {player_count+1} name (leave blank to stop): ").strip()
            if not ai_name:
                break
            
            # Get AI difficulty
            while True:
                try:
                    aggression = float(input(f"Aggression level for {ai_name} (0.0-1.0): "))
                    if 0.0 <= aggression <= 1.0:
                        break
                    print("Value must be between 0.0 and 1.0")
                except ValueError:
                    print("Please enter a valid number")
            
            while True:
                try:
                    bluff = float(input(f"Bluff factor for {ai_name} (0.0-1.0): "))
                    if 0.0 <= bluff <= 1.0:
                        break
                    print("Value must be between 0.0 and 1.0")
                except ValueError:
                    print("Please enter a valid number")
            
            from just_a_poker_game.ai.basic_ai import BasicAIPlayer
            players.append(BasicAIPlayer(ai_name, starting_chips, aggression, bluff))
            player_count += 1
        
        if len(players) < 2:
            print("At least 2 players are required. Adding default AI player.")
            from just_a_poker_game.ai.basic_ai import BasicAIPlayer
            players.append(BasicAIPlayer("AI Player", starting_chips))
        
        print()
        print(f"Player setup complete. {len(players)} players added.")
        input("Press Enter to continue...")
        
        return players
