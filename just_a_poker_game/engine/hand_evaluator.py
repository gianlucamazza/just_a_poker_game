"""
Hand evaluation module for poker game.

This module contains classes and functions to evaluate poker hands
and determine their ranking.
"""
from enum import Enum, auto
from typing import List, Tuple, Dict, Set, Optional
from collections import Counter

from just_a_poker_game.engine.card import Card, Rank, Suit


class HandRank(Enum):
    """Enum for poker hand rankings."""
    HIGH_CARD = auto()
    PAIR = auto()
    TWO_PAIR = auto()
    THREE_OF_A_KIND = auto()
    STRAIGHT = auto()
    FLUSH = auto()
    FULL_HOUSE = auto()
    FOUR_OF_A_KIND = auto()
    STRAIGHT_FLUSH = auto()
    ROYAL_FLUSH = auto()
    
    def __lt__(self, other):
        if not isinstance(other, HandRank):
            return NotImplemented
        return self.value < other.value


class HandEvaluator:
    """
    Evaluates poker hands to determine their ranking.
    """
    
    @staticmethod
    def evaluate(hole_cards: List[Card], community_cards: List[Card]) -> Tuple[HandRank, List[Card]]:
        """
        Evaluate the best possible hand from hole cards and community cards.
        
        Args:
            hole_cards: A player's hole cards (2 cards in Texas Hold'em)
            community_cards: The community cards (up to 5 cards)
            
        Returns:
            Tuple containing the hand rank and the 5 cards that make the best hand
        """
        all_cards = hole_cards + community_cards
        return HandEvaluator._find_best_hand(all_cards)
    
    @staticmethod
    def _find_best_hand(cards: List[Card]) -> Tuple[HandRank, List[Card]]:
        """
        Find the highest-ranking 5-card hand from a collection of cards.
        
        Args:
            cards: Collection of cards to evaluate
            
        Returns:
            Tuple containing the hand rank and the 5 cards that make the best hand
        """
        # Check for at least 5 cards
        if len(cards) < 5:
            raise ValueError("At least 5 cards are required to evaluate a hand")
        
        # Sort cards by rank (highest first)
        sorted_cards = sorted(cards, key=lambda card: card.rank.value, reverse=True)
        
        # Check for royal flush, straight flush, and flush
        flush_cards = HandEvaluator._find_flush(sorted_cards)
        if flush_cards:
            # Check for straight flush or royal flush
            straight_flush = HandEvaluator._find_straight(flush_cards)
            if straight_flush:
                if straight_flush[0].rank == Rank.ACE:
                    return HandRank.ROYAL_FLUSH, straight_flush
                return HandRank.STRAIGHT_FLUSH, straight_flush
            return HandRank.FLUSH, flush_cards[:5]
        
        # Check for straight
        straight_cards = HandEvaluator._find_straight(sorted_cards)
        if straight_cards:
            return HandRank.STRAIGHT, straight_cards
        
        # Count card frequencies by rank
        card_count = Counter()
        for card in sorted_cards:
            card_count[card.rank.value] += 1
        
        # Check for four of a kind
        four_of_a_kind = HandEvaluator._find_n_of_a_kind(sorted_cards, card_count, 4)
        if four_of_a_kind:
            return HandRank.FOUR_OF_A_KIND, four_of_a_kind
        
        # Check for full house
        full_house = HandEvaluator._find_full_house(sorted_cards, card_count)
        if full_house:
            return HandRank.FULL_HOUSE, full_house
        
        # Check for three of a kind
        three_of_a_kind = HandEvaluator._find_n_of_a_kind(sorted_cards, card_count, 3)
        if three_of_a_kind:
            return HandRank.THREE_OF_A_KIND, three_of_a_kind
        
        # Check for two pair
        two_pair = HandEvaluator._find_two_pair(sorted_cards, card_count)
        if two_pair:
            return HandRank.TWO_PAIR, two_pair
        
        # Check for one pair
        one_pair = HandEvaluator._find_n_of_a_kind(sorted_cards, card_count, 2)
        if one_pair:
            return HandRank.PAIR, one_pair
        
        # High card
        return HandRank.HIGH_CARD, sorted_cards[:5]
    
    @staticmethod
    def _find_flush(cards: List[Card]) -> Optional[List[Card]]:
        """Find the highest flush in the card collection."""
        suits = {}
        for card in cards:
            if card.suit not in suits:
                suits[card.suit] = []
            suits[card.suit].append(card)
        
        # Check if we have a flush (5+ cards of the same suit)
        for suit, suited_cards in suits.items():
            if len(suited_cards) >= 5:
                # Return the 5 highest cards of the flush suit
                return sorted(suited_cards, key=lambda card: card.rank.value, reverse=True)[:5]
        
        return None
    
    @staticmethod
    def _find_straight(cards: List[Card]) -> Optional[List[Card]]:
        """Find the highest straight in the card collection."""
        if not cards:
            return None
        
        # Remove duplicate ranks
        unique_ranks = []
        prev_rank = None
        for card in cards:
            if card.rank != prev_rank:
                unique_ranks.append(card)
                prev_rank = card.rank
        
        # Check for straights
        for i in range(len(unique_ranks) - 4):
            if (unique_ranks[i].rank.value - unique_ranks[i + 4].rank.value == 4):
                return unique_ranks[i:i + 5]
        
        # Special case: A-5-4-3-2 straight (Ace is low)
        # Check if we have an Ace
        if unique_ranks and unique_ranks[0].rank == Rank.ACE:
            # Look for 5-4-3-2
            low_straight = True
            for i, rank_val in enumerate([5, 4, 3, 2]):
                if not any(card.rank.value == rank_val for card in unique_ranks):
                    low_straight = False
                    break
            
            if low_straight:
                # Construct the wheel straight (5-4-3-2-A)
                wheel = [next(card for card in unique_ranks if card.rank.value == rank_val) 
                        for rank_val in [5, 4, 3, 2]]
                # Add the Ace as the low card
                wheel.append(next(card for card in unique_ranks if card.rank == Rank.ACE))
                return wheel
        
        return None
    
    @staticmethod
    def _find_n_of_a_kind(cards: List[Card], card_count: Counter, n: int) -> Optional[List[Card]]:
        """Find n cards of the same rank (plus high cards to make 5)."""
        # Find the highest rank with n cards
        for rank_val, count in sorted(card_count.items(), reverse=True):
            if count >= n:
                # Get the n cards of this rank
                matched = [card for card in cards if card.rank.value == rank_val][:n]
                
                # Add high cards to complete the hand (that aren't part of the n of a kind)
                remaining = [card for card in cards if card.rank.value != rank_val]
                matched.extend(remaining[:5 - n])
                
                return matched
        
        return None
    
    @staticmethod
    def _find_full_house(cards: List[Card], card_count: Counter) -> Optional[List[Card]]:
        """Find a full house (three of a kind + pair)."""
        # Find the highest rank with 3 or more cards for the three of a kind part
        three_of_a_kind_rank = None
        for rank_val, count in sorted(card_count.items(), reverse=True):
            if count >= 3:
                three_of_a_kind_rank = rank_val
                break
        
        if three_of_a_kind_rank is None:
            return None
        
        # Find the highest rank with 2 or more cards for the pair part (different from three of a kind rank)
        pair_rank = None
        for rank_val, count in sorted(card_count.items(), reverse=True):
            if rank_val != three_of_a_kind_rank and count >= 2:
                pair_rank = rank_val
                break
        
        if pair_rank is None:
            return None
        
        # Get the cards for the full house
        three_cards = [card for card in cards if card.rank.value == three_of_a_kind_rank][:3]
        pair_cards = [card for card in cards if card.rank.value == pair_rank][:2]
        
        return three_cards + pair_cards
    
    @staticmethod
    def _find_two_pair(cards: List[Card], card_count: Counter) -> Optional[List[Card]]:
        """Find two pair (plus a high card to make 5)."""
        pairs = []
        # Find the two highest ranks with pairs
        for rank_val, count in sorted(card_count.items(), reverse=True):
            if count >= 2:
                # Get the pair cards of this rank
                pair = [card for card in cards if card.rank.value == rank_val][:2]
                pairs.extend(pair)
                
                # If we have two pairs, we're done looking for pairs
                if len(pairs) == 4:
                    break
        
        if len(pairs) != 4:
            return None
        
        # Add the highest remaining card that's not part of either pair
        pair_ranks = {card.rank.value for card in pairs}
        for card in cards:
            if card.rank.value not in pair_ranks:
                pairs.append(card)
                break
        
        return pairs
