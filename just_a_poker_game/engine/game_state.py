"""
Game state module for poker game.

This module manages the state of the poker game including betting rounds,
pot management, and game progression.
"""
from enum import Enum, auto
from typing import List, Dict, Optional, Tuple
import logging

from just_a_poker_game.engine.card import Card, Deck
from just_a_poker_game.engine.hand_evaluator import HandEvaluator, HandRank
from just_a_poker_game.player.player import Player


logger = logging.getLogger(__name__)


class BettingRound(Enum):
    """Enum for poker betting rounds."""
    PREFLOP = auto()
    FLOP = auto()
    TURN = auto()
    RIVER = auto()
    SHOWDOWN = auto()


class GameState:
    """
    Manages the state of a poker game.
    
    Attributes:
        players (List[Player]): List of players in the game.
        deck (Deck): The current deck of cards.
        community_cards (List[Card]): The community cards on the table.
        pot (int): The current pot size.
        current_bet (int): The current bet amount that players need to match.
        min_raise (int): The minimum raise amount.
        small_blind (int): The small blind amount.
        big_blind (int): The big blind amount.
        dealer_position (int): The position of the dealer button.
        current_position (int): The position of the current player to act.
        betting_round (BettingRound): The current betting round.
        active_players (List[Player]): Players still in the hand.
    """
    
    def __init__(self, players: List[Player], small_blind: int = 1, big_blind: int = 2):
        """
        Initialize a new game state.
        
        Args:
            players: List of players in the game.
            small_blind: The small blind amount.
            big_blind: The big blind amount.
        """
        if len(players) < 2:
            raise ValueError("At least 2 players are required")
        
        self.players = players
        self.deck = Deck()
        self.community_cards: List[Card] = []
        self.pot = 0
        self.current_bet = 0
        self.min_raise = big_blind
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.dealer_position = 0
        self.current_position = 0
        self.betting_round = BettingRound.PREFLOP
        self.active_players = list(players)  # Copy the list
        self.last_aggressor = None  # Tracks the last player who bet or raised
    
    def start_hand(self):
        """Start a new hand, dealing cards and setting up the initial state."""
        # Reset state
        self.deck = Deck()
        self.deck.shuffle()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.betting_round = BettingRound.PREFLOP
        
        # Reset player states
        for player in self.players:
            player.folded = False
            player.hand = []
            player.bet = 0
        
        # Reset active players
        self.active_players = [p for p in self.players if p.chips > 0]
        
        # Move the dealer button
        self.dealer_position = (self.dealer_position + 1) % len(self.players)
        
        # Deal hole cards to each player
        for _ in range(2):
            for player in self.active_players:
                player.hand.append(self.deck.deal())
        
        # Set up blinds
        self._post_blinds()
        
        # Set the current position to first player to act
        self._set_first_to_act()
    
    def _post_blinds(self):
        """Post the small and big blinds."""
        if len(self.active_players) >= 2:
            # Small blind position
            sb_pos = (self.dealer_position + 1) % len(self.active_players)
            sb_player = self.active_players[sb_pos]
            sb_amount = min(self.small_blind, sb_player.chips)
            sb_player.bet = sb_amount
            sb_player.chips -= sb_amount
            
            # Big blind position
            bb_pos = (self.dealer_position + 2) % len(self.active_players)
            bb_player = self.active_players[bb_pos]
            bb_amount = min(self.big_blind, bb_player.chips)
            bb_player.bet = bb_amount
            bb_player.chips -= bb_amount
            
            # Set current bet to big blind
            self.current_bet = bb_amount
            self.min_raise = self.big_blind
        else:
            # Heads-up play (only 2 players)
            # Dealer posts small blind
            sb_player = self.active_players[self.dealer_position]
            sb_amount = min(self.small_blind, sb_player.chips)
            sb_player.bet = sb_amount
            sb_player.chips -= sb_amount
            
            # Non-dealer posts big blind
            bb_pos = (self.dealer_position + 1) % len(self.active_players)
            bb_player = self.active_players[bb_pos]
            bb_amount = min(self.big_blind, bb_player.chips)
            bb_player.bet = bb_amount
            bb_player.chips -= bb_amount
            
            # Set current bet to big blind
            self.current_bet = bb_amount
            self.min_raise = self.big_blind
    
    def _set_first_to_act(self):
        """Set the first player to act based on the betting round."""
        if self.betting_round == BettingRound.PREFLOP:
            # First to act is player after big blind
            self.current_position = (self.dealer_position + 3) % len(self.active_players)
        else:
            # First to act is player after dealer
            self.current_position = (self.dealer_position + 1) % len(self.active_players)
        
        # Make sure we skip folded players
        self._advance_to_next_active_player()
    
    def _advance_to_next_active_player(self):
        """Advance to the next active player that hasn't folded."""
        initial_pos = self.current_position
        
        while True:
            self.current_position = (self.current_position + 1) % len(self.players)
            
            # If we've gone all the way around, stop
            if self.current_position == initial_pos:
                break
            
            # Check if the player is active and has chips
            if (self.players[self.current_position] in self.active_players and 
                not self.players[self.current_position].folded and
                self.players[self.current_position].chips > 0):
                break
    
    def get_current_player(self) -> Player:
        """Get the current player to act."""
        return self.players[self.current_position]
    
    def player_action(self, action: str, amount: int = 0) -> bool:
        """
        Process a player's action.
        
        Args:
            action: The action type ('fold', 'check', 'call', 'bet', 'raise', 'all-in')
            amount: The amount for bets and raises
            
        Returns:
            bool: True if the betting round is over, False otherwise
        """
        player = self.get_current_player()
        
        if action == 'fold':
            player.folded = True
            self.active_players.remove(player)
            logger.info(f"{player.name} folds")
            
            # Check if only one player remains
            if len(self.active_players) == 1:
                return True
        
        elif action == 'check':
            # Can only check if no current bet
            if self.current_bet > player.bet:
                raise ValueError("Cannot check when there's a bet to call")
            logger.info(f"{player.name} checks")
        
        elif action == 'call':
            # Calculate how much more the player needs to add
            call_amount = min(self.current_bet - player.bet, player.chips)
            player.chips -= call_amount
            player.bet += call_amount
            logger.info(f"{player.name} calls {call_amount}")
        
        elif action == 'bet':
            # Can only bet if no current bet
            if self.current_bet > 0:
                raise ValueError("Cannot bet when there's already a bet (use raise)")
            
            # Ensure bet meets minimum
            if amount < self.big_blind:
                amount = self.big_blind
            
            amount = min(amount, player.chips)  # Cap at available chips
            player.chips -= amount
            player.bet += amount
            self.current_bet = amount
            self.min_raise = amount
            self.last_aggressor = player
            logger.info(f"{player.name} bets {amount}")
        
        elif action == 'raise':
            # Ensure raise meets minimum
            if self.current_bet == 0:
                raise ValueError("Cannot raise when there's no bet (use bet)")
            
            # Calculate minimum and maximum raise
            min_raise_to = self.current_bet + self.min_raise
            if amount < min_raise_to:
                amount = min_raise_to
            
            amount = min(amount, player.chips + player.bet)  # Cap at available chips
            raise_amount = amount - player.bet
            player.chips -= raise_amount
            player.bet = amount
            self.current_bet = amount
            self.min_raise = amount - self.current_bet  # Update min raise
            self.last_aggressor = player
            logger.info(f"{player.name} raises to {amount}")
        
        elif action == 'all-in':
            all_in_amount = player.chips + player.bet
            player.chips = 0
            
            if all_in_amount > self.current_bet:
                # All-in is a raise
                if all_in_amount - self.current_bet >= self.min_raise:
                    # This is a valid raise, update the minimum raise amount
                    self.min_raise = all_in_amount - self.current_bet
                self.current_bet = all_in_amount
                self.last_aggressor = player
            
            player.bet = all_in_amount
            logger.info(f"{player.name} is all-in for {all_in_amount}")
        
        else:
            raise ValueError(f"Unknown action: {action}")
        
        # Move to the next player
        self._advance_to_next_active_player()
        
        # Check if the betting round is complete
        return self._is_betting_round_complete()
    
    def _is_betting_round_complete(self) -> bool:
        """
        Check if the current betting round is complete.
        
        Returns:
            bool: True if complete, False otherwise
        """
        # If only one player remains, round is complete
        if len(self.active_players) == 1:
            return True
        
        # Check if all active players have acted and all bets are matched
        all_bets_matched = all(p.bet == self.current_bet or p.chips == 0 for p in self.active_players)
        all_players_acted = (self.last_aggressor is None or 
                            self.current_position == self.players.index(self.last_aggressor))
        
        return all_bets_matched and all_players_acted
    
    def next_betting_round(self) -> bool:
        """
        Move to the next betting round.
        
        Returns:
            bool: True if the hand is complete, False otherwise
        """
        # Collect bets into the pot
        for player in self.players:
            self.pot += player.bet
            player.bet = 0
        
        # Reset betting state
        self.current_bet = 0
        self.last_aggressor = None
        
        # Move to the next round
        if self.betting_round == BettingRound.PREFLOP:
            self.betting_round = BettingRound.FLOP
            self._deal_community_cards(3)  # Deal the flop
        elif self.betting_round == BettingRound.FLOP:
            self.betting_round = BettingRound.TURN
            self._deal_community_cards(1)  # Deal the turn
        elif self.betting_round == BettingRound.TURN:
            self.betting_round = BettingRound.RIVER
            self._deal_community_cards(1)  # Deal the river
        elif self.betting_round == BettingRound.RIVER:
            self.betting_round = BettingRound.SHOWDOWN
            return True  # Hand is complete, go to showdown
        
        # Set first player to act
        self._set_first_to_act()
        return False
    
    def _deal_community_cards(self, count: int):
        """Deal community cards."""
        self.community_cards.extend(self.deck.deal_multiple(count))
    
    def showdown(self) -> List[Tuple[Player, HandRank, List[Card]]]:
        """
        Evaluate hands and determine winners.
        
        Returns:
            List of tuples (player, hand_rank, best_cards) for each active player
        """
        results = []
        for player in self.active_players:
            hand_rank, best_cards = HandEvaluator.evaluate(player.hand, self.community_cards)
            results.append((player, hand_rank, best_cards))
        
        # Sort by hand rank (highest first)
        results.sort(key=lambda x: x[1].value, reverse=True)
        return results
    
    def award_pot(self, winners: List[Player]):
        """Award the pot to the winners."""
        if not winners:
            return
        
        pot_per_winner = self.pot // len(winners)
        remainder = self.pot % len(winners)
        
        for i, player in enumerate(winners):
            award = pot_per_winner
            if i < remainder:
                award += 1
            player.chips += award
            logger.info(f"{player.name} wins {award} chips")
        
        self.pot = 0
