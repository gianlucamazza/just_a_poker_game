"""
Player module for poker game.

This module defines the base player class and its implementations
for human and AI players.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Tuple
import logging
import uuid

from just_a_poker_game.engine.card import Card


logger = logging.getLogger(__name__)


class Player(ABC):
    """
    Abstract base class for poker players.
    
    Attributes:
        name (str): Player's name.
        chips (int): Player's chip count.
        hand (List[Card]): Player's hole cards.
        folded (bool): Whether the player has folded the current hand.
        bet (int): Player's current bet in the betting round.
        player_id (str): Unique identifier for the player.
    """
    
    def __init__(self, name: str, chips: int = 1000):
        """
        Initialize a player.
        
        Args:
            name: Player's name.
            chips: Starting chip count.
        """
        self.name = name
        self.chips = chips
        self.hand: List[Card] = []
        self.folded = False
        self.bet = 0
        self.player_id = str(uuid.uuid4())
        self.total_hands_played = 0
        self.hands_won = 0
        self.biggest_pot_won = 0
    
    def get_action(self, game_state) -> Tuple[str, int]:
        """
        Get the player's action.
        
        Args:
            game_state: The current game state.
            
        Returns:
            Tuple of (action_type, amount)
            action_type can be: 'fold', 'check', 'call', 'bet', 'raise', 'all-in'
        """
        if self.chips == 0:
            return 'all-in', 0
        
        action, amount = self._get_action_impl(game_state)
        
        # Validate action
        current_bet = game_state.current_bet
        player_bet = self.bet
        
        if action == 'fold':
            return action, 0
        
        elif action == 'check':
            if current_bet > player_bet:
                logger.warning(f"Invalid check from {self.name}, converting to fold")
                return 'fold', 0
            return action, 0
        
        elif action == 'call':
            return action, 0  # Amount is calculated in game state
        
        elif action == 'bet':
            if current_bet > 0:
                logger.warning(f"Invalid bet from {self.name}, converting to raise")
                action = 'raise'
            amount = max(amount, game_state.big_blind)
            amount = min(amount, self.chips)
            return action, amount
        
        elif action == 'raise':
            if current_bet == 0:
                logger.warning(f"Invalid raise from {self.name}, converting to bet")
                action = 'bet'
                amount = max(amount, game_state.big_blind)
            else:
                min_raise = current_bet + game_state.min_raise
                if amount < min_raise:
                    amount = min_raise
            amount = min(amount, self.chips + player_bet)
            return action, amount
        
        elif action == 'all-in':
            return action, 0  # Amount is calculated in game state
        
        # Default to folding for invalid actions
        logger.warning(f"Invalid action '{action}' from {self.name}, converting to fold")
        return 'fold', 0
    
    @abstractmethod
    def _get_action_impl(self, game_state) -> Tuple[str, int]:
        """
        Implementation for getting the player's action.
        
        Args:
            game_state: The current game state.
            
        Returns:
            Tuple of (action_type, amount)
        """
        pass
    
    def update_stats(self, won_hand: bool, pot_size: int = 0):
        """
        Update player statistics.
        
        Args:
            won_hand: Whether the player won the hand.
            pot_size: Size of the pot if the player won.
        """
        self.total_hands_played += 1
        
        if won_hand:
            self.hands_won += 1
            if pot_size > self.biggest_pot_won:
                self.biggest_pot_won = pot_size
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert player to a dictionary for storage.
        
        Returns:
            Dictionary representation of the player.
        """
        return {
            'player_id': self.player_id,
            'name': self.name,
            'chips': self.chips,
            'total_hands_played': self.total_hands_played,
            'hands_won': self.hands_won,
            'biggest_pot_won': self.biggest_pot_won
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
        """
        Create a player from a dictionary.
        
        Args:
            data: Dictionary with player data.
            
        Returns:
            New Player instance.
        """
        # This will be implemented by subclasses
        raise NotImplementedError("Subclasses must implement from_dict")
    
    def __str__(self) -> str:
        return f"{self.name} ({self.chips} chips)"


class HumanPlayer(Player):
    """Human player implementation that takes input from the UI."""
    
    def _get_action_impl(self, game_state) -> Tuple[str, int]:
        """
        Get action from the UI.
        
        Args:
            game_state: The current game state.
            
        Returns:
            Tuple of (action_type, amount)
        """
        # This will be implemented by the UI
        # For now, we'll just return a placeholder
        return 'fold', 0
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HumanPlayer':
        """Create a HumanPlayer from a dictionary."""
        player = cls(data['name'], data['chips'])
        player.player_id = data['player_id']
        player.total_hands_played = data.get('total_hands_played', 0)
        player.hands_won = data.get('hands_won', 0)
        player.biggest_pot_won = data.get('biggest_pot_won', 0)
        return player
