"""
Basic AI player implementation.

This module provides a simple AI player that uses basic heuristics
to make decisions in the poker game.
"""
import random
from typing import Tuple, Dict, Any
import logging

from just_a_poker_game.player.player import Player
from just_a_poker_game.engine.hand_evaluator import HandEvaluator, HandRank


logger = logging.getLogger(__name__)


class BasicAIPlayer(Player):
    """
    Basic AI player that uses simple strategies.
    
    Attributes:
        aggression (float): How aggressive the AI plays (0.0-1.0).
        bluff_factor (float): Likelihood of bluffing (0.0-1.0).
    """
    
    def __init__(self, name: str, chips: int = 1000, 
                 aggression: float = 0.5, bluff_factor: float = 0.2):
        """
        Initialize a basic AI player.
        
        Args:
            name: AI player's name.
            chips: Starting chips.
            aggression: Aggression factor (0.0-1.0).
            bluff_factor: Bluff likelihood (0.0-1.0).
        """
        super().__init__(name, chips)
        self.aggression = max(0.0, min(1.0, aggression))
        self.bluff_factor = max(0.0, min(1.0, bluff_factor))
    
    def _get_action_impl(self, game_state) -> Tuple[str, int]:
        """
        Determine the AI's action.
        
        Args:
            game_state: Current game state.
            
        Returns:
            Tuple of (action_type, amount)
        """
        # Evaluate current hand strength
        hand_strength = self._evaluate_hand_strength(game_state)
        
        # Check if we're bluffing this round
        is_bluffing = random.random() < self.bluff_factor
        
        # Modify hand strength based on bluffing
        if is_bluffing:
            hand_strength = 0.8 if hand_strength < 0.5 else 0.2
        
        # Get betting round position
        position = self._get_position_type(game_state)
        
        # Determine action based on hand strength, position, and game state
        return self._decide_action(game_state, hand_strength, position, is_bluffing)
    
    def _evaluate_hand_strength(self, game_state) -> float:
        """
        Evaluate the current hand strength.
        
        Args:
            game_state: Current game state.
            
        Returns:
            Float value between 0.0 (weak) and 1.0 (strong).
        """
        # Base evaluation on the current community cards
        if not game_state.community_cards:
            # Preflop: evaluate based on hole cards only
            return self._evaluate_preflop()
        else:
            # Postflop: use hand evaluator
            hand_rank, _ = HandEvaluator.evaluate(self.hand, game_state.community_cards)
            
            # Scale based on hand rank
            return self._scale_hand_rank(hand_rank, len(game_state.community_cards))
    
    def _evaluate_preflop(self) -> float:
        """
        Evaluate preflop hand strength.
        
        Returns:
            Float value between 0.0 (weak) and 1.0 (strong).
        """
        if len(self.hand) != 2:
            return 0.0
        
        card1, card2 = self.hand
        
        # Pair
        if card1.rank == card2.rank:
            rank_value = card1.rank.value
            # Scale from 0.5 (2s) to 1.0 (Aces)
            return 0.5 + (rank_value - 2) / 24
        
        # Suited cards
        suited = card1.suit == card2.suit
        
        # Calculate value based on ranks
        high_card = max(card1.rank.value, card2.rank.value)
        low_card = min(card1.rank.value, card2.rank.value)
        gap = high_card - low_card
        
        # Base value for high cards
        value = (high_card - 2) / 12 * 0.5
        
        # Connected cards are better
        if gap == 1:
            value += 0.1
        elif gap == 2:
            value += 0.05
        
        # Suited cards are better
        if suited:
            value += 0.2
        
        # Cap the value
        return min(0.85, max(0.1, value))
    
    def _scale_hand_rank(self, hand_rank: HandRank, community_card_count: int) -> float:
        """
        Scale the hand rank to a strength value.
        
        Args:
            hand_rank: The current hand rank.
            community_card_count: Number of community cards.
            
        Returns:
            Float value between 0.0 (weak) and 1.0 (strong).
        """
        # Base strength on hand rank
        rank_strengths = {
            HandRank.HIGH_CARD: 0.1,
            HandRank.PAIR: 0.2,
            HandRank.TWO_PAIR: 0.4,
            HandRank.THREE_OF_A_KIND: 0.6,
            HandRank.STRAIGHT: 0.7,
            HandRank.FLUSH: 0.8,
            HandRank.FULL_HOUSE: 0.9,
            HandRank.FOUR_OF_A_KIND: 0.95,
            HandRank.STRAIGHT_FLUSH: 0.98,
            HandRank.ROYAL_FLUSH: 1.0
        }
        
        # Get base strength
        strength = rank_strengths.get(hand_rank, 0.0)
        
        # Adjust based on stage (more community cards means more certainty)
        certainty_factor = community_card_count / 5
        adjusted_strength = strength * certainty_factor + strength * (1 - certainty_factor) * 0.8
        
        return adjusted_strength
    
    def _get_position_type(self, game_state) -> str:
        """
        Determine position type (early, middle, late).
        
        Args:
            game_state: Current game state.
            
        Returns:
            Position type as string.
        """
        num_active = len(game_state.active_players)
        player_position = game_state.players.index(self)
        dealer_position = game_state.dealer_position
        
        # Calculate relative position
        relative_position = (player_position - dealer_position) % num_active
        
        # Determine position type
        if relative_position < num_active // 3:
            return "early"
        elif relative_position < 2 * num_active // 3:
            return "middle"
        else:
            return "late"
    
    def _decide_action(self, game_state, hand_strength: float, 
                      position: str, is_bluffing: bool) -> Tuple[str, int]:
        """
        Decide on the action to take.
        
        Args:
            game_state: Current game state.
            hand_strength: Evaluated hand strength (0.0-1.0).
            position: Position type (early, middle, late).
            is_bluffing: Whether the AI is bluffing.
            
        Returns:
            Tuple of (action_type, amount)
        """
        # Current game state
        current_bet = game_state.current_bet
        pot_size = game_state.pot + sum(p.bet for p in game_state.players)
        call_amount = current_bet - self.bet
        
        # Check if we can check
        can_check = call_amount == 0
        
        # Position modifiers
        position_mod = {
            "early": -0.1,
            "middle": 0.0,
            "late": 0.1
        }
        
        # Modify hand strength based on position
        adjusted_strength = hand_strength + position_mod.get(position, 0.0)
        
        # Further adjust based on aggression factor
        adjusted_strength = adjusted_strength * (1.0 - self.aggression) + self.aggression
        
        # Make decision
        if adjusted_strength > 0.8:
            # Strong hand: bet or raise
            if can_check:
                if random.random() < 0.3:
                    return 'check', 0  # Slow play occasionally
                else:
                    bet_amount = int(pot_size * (0.5 + random.random() * 0.5))
                    return 'bet', bet_amount
            else:
                raise_amount = int(current_bet * 2.5 + random.random() * pot_size * 0.2)
                if raise_amount > self.chips:
                    return 'all-in', 0
                return 'raise', raise_amount
        
        elif adjusted_strength > 0.5:
            # Medium hand: call or small raise
            if can_check:
                if random.random() < 0.7:
                    return 'check', 0
                else:
                    bet_amount = int(pot_size * 0.5)
                    return 'bet', bet_amount
            else:
                if call_amount / pot_size < 0.2 or is_bluffing:
                    if random.random() < 0.3:
                        raise_amount = int(current_bet * 1.5)
                        return 'raise', raise_amount
                    return 'call', 0
                else:
                    return 'fold', 0
        
        elif adjusted_strength > 0.3:
            # Weak hand: check or call small bets
            if can_check:
                return 'check', 0
            else:
                if call_amount / pot_size < 0.1 or is_bluffing:
                    return 'call', 0
                else:
                    return 'fold', 0
        
        else:
            # Very weak hand: check or fold
            if can_check:
                if random.random() < 0.1 and position == "late":
                    # Occasionally bluff in late position
                    bet_amount = int(pot_size * 0.3)
                    return 'bet', bet_amount
                return 'check', 0
            else:
                # Maybe call very small bets
                if call_amount / pot_size < 0.05 and is_bluffing:
                    return 'call', 0
                return 'fold', 0
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BasicAIPlayer':
        """Create a BasicAIPlayer from a dictionary."""
        player = cls(
            data['name'], 
            data['chips'],
            data.get('aggression', 0.5),
            data.get('bluff_factor', 0.2)
        )
        player.player_id = data['player_id']
        player.total_hands_played = data.get('total_hands_played', 0)
        player.hands_won = data.get('hands_won', 0)
        player.biggest_pot_won = data.get('biggest_pot_won', 0)
        return player
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert player to a dictionary for storage."""
        data = super().to_dict()
        data.update({
            'aggression': self.aggression,
            'bluff_factor': self.bluff_factor,
            'type': 'ai'
        })
        return data
