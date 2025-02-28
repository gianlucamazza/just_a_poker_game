"""
Tests for the hand evaluator module.
"""
import unittest
from just_a_poker_game.engine.card import Card, Rank, Suit
from just_a_poker_game.engine.hand_evaluator import HandEvaluator, HandRank


class TestHandEvaluator(unittest.TestCase):
    """Test cases for HandEvaluator class."""
    
    def test_royal_flush(self):
        """Test royal flush detection."""
        # A, K, Q, J, 10 of hearts
        cards = [
            Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.KING, Suit.HEARTS),
            Card(Rank.QUEEN, Suit.HEARTS),
            Card(Rank.JACK, Suit.HEARTS),
            Card(Rank.TEN, Suit.HEARTS),
            Card(Rank.TWO, Suit.CLUBS),
            Card(Rank.THREE, Suit.DIAMONDS)
        ]
        
        hand_rank, best_cards = HandEvaluator._find_best_hand(cards)
        self.assertEqual(hand_rank, HandRank.ROYAL_FLUSH)
        self.assertEqual(len(best_cards), 5)
    
    def test_straight_flush(self):
        """Test straight flush detection."""
        # 9, 8, 7, 6, 5 of spades
        cards = [
            Card(Rank.NINE, Suit.SPADES),
            Card(Rank.EIGHT, Suit.SPADES),
            Card(Rank.SEVEN, Suit.SPADES),
            Card(Rank.SIX, Suit.SPADES),
            Card(Rank.FIVE, Suit.SPADES),
            Card(Rank.TWO, Suit.CLUBS),
            Card(Rank.THREE, Suit.DIAMONDS)
        ]
        
        hand_rank, best_cards = HandEvaluator._find_best_hand(cards)
        self.assertEqual(hand_rank, HandRank.STRAIGHT_FLUSH)
        self.assertEqual(len(best_cards), 5)
    
    def test_four_of_a_kind(self):
        """Test four of a kind detection."""
        # Four 8s and a King
        cards = [
            Card(Rank.EIGHT, Suit.HEARTS),
            Card(Rank.EIGHT, Suit.DIAMONDS),
            Card(Rank.EIGHT, Suit.CLUBS),
            Card(Rank.EIGHT, Suit.SPADES),
            Card(Rank.KING, Suit.HEARTS),
            Card(Rank.TWO, Suit.CLUBS),
            Card(Rank.THREE, Suit.DIAMONDS)
        ]
        
        hand_rank, best_cards = HandEvaluator._find_best_hand(cards)
        self.assertEqual(hand_rank, HandRank.FOUR_OF_A_KIND)
        self.assertEqual(len(best_cards), 5)
    
    def test_full_house(self):
        """Test full house detection."""
        # Three 7s and two Queens
        cards = [
            Card(Rank.SEVEN, Suit.HEARTS),
            Card(Rank.SEVEN, Suit.DIAMONDS),
            Card(Rank.SEVEN, Suit.CLUBS),
            Card(Rank.QUEEN, Suit.HEARTS),
            Card(Rank.QUEEN, Suit.SPADES),
            Card(Rank.TWO, Suit.CLUBS),
            Card(Rank.THREE, Suit.DIAMONDS)
        ]
        
        hand_rank, best_cards = HandEvaluator._find_best_hand(cards)
        self.assertEqual(hand_rank, HandRank.FULL_HOUSE)
        self.assertEqual(len(best_cards), 5)
    
    def test_flush(self):
        """Test flush detection."""
        # Five hearts, not in sequence
        cards = [
            Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.JACK, Suit.HEARTS),
            Card(Rank.NINE, Suit.HEARTS),
            Card(Rank.SEVEN, Suit.HEARTS),
            Card(Rank.THREE, Suit.HEARTS),
            Card(Rank.TWO, Suit.CLUBS),
            Card(Rank.THREE, Suit.DIAMONDS)
        ]
        
        hand_rank, best_cards = HandEvaluator._find_best_hand(cards)
        self.assertEqual(hand_rank, HandRank.FLUSH)
        self.assertEqual(len(best_cards), 5)
    
    def test_straight(self):
        """Test straight detection."""
        # 10, 9, 8, 7, 6 of mixed suits
        cards = [
            Card(Rank.TEN, Suit.HEARTS),
            Card(Rank.NINE, Suit.DIAMONDS),
            Card(Rank.EIGHT, Suit.CLUBS),
            Card(Rank.SEVEN, Suit.HEARTS),
            Card(Rank.SIX, Suit.SPADES),
            Card(Rank.TWO, Suit.CLUBS),
            Card(Rank.THREE, Suit.DIAMONDS)
        ]
        
        hand_rank, best_cards = HandEvaluator._find_best_hand(cards)
        self.assertEqual(hand_rank, HandRank.STRAIGHT)
        self.assertEqual(len(best_cards), 5)
    
    def test_three_of_a_kind(self):
        """Test three of a kind detection."""
        # Three Jacks
        cards = [
            Card(Rank.JACK, Suit.HEARTS),
            Card(Rank.JACK, Suit.DIAMONDS),
            Card(Rank.JACK, Suit.CLUBS),
            Card(Rank.NINE, Suit.HEARTS),
            Card(Rank.FIVE, Suit.SPADES),
            Card(Rank.TWO, Suit.CLUBS),
            Card(Rank.THREE, Suit.DIAMONDS)
        ]
        
        hand_rank, best_cards = HandEvaluator._find_best_hand(cards)
        self.assertEqual(hand_rank, HandRank.THREE_OF_A_KIND)
        self.assertEqual(len(best_cards), 5)
    
    def test_two_pair(self):
        """Test two pair detection."""
        # Pair of Aces and pair of Queens
        cards = [
            Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.ACE, Suit.DIAMONDS),
            Card(Rank.QUEEN, Suit.CLUBS),
            Card(Rank.QUEEN, Suit.HEARTS),
            Card(Rank.FIVE, Suit.SPADES),
            Card(Rank.TWO, Suit.CLUBS),
            Card(Rank.THREE, Suit.DIAMONDS)
        ]
        
        hand_rank, best_cards = HandEvaluator._find_best_hand(cards)
        self.assertEqual(hand_rank, HandRank.TWO_PAIR)
        self.assertEqual(len(best_cards), 5)
    
    def test_pair(self):
        """Test one pair detection."""
        # Pair of Kings
        cards = [
            Card(Rank.KING, Suit.HEARTS),
            Card(Rank.KING, Suit.DIAMONDS),
            Card(Rank.QUEEN, Suit.CLUBS),
            Card(Rank.JACK, Suit.HEARTS),
            Card(Rank.FIVE, Suit.SPADES),
            Card(Rank.TWO, Suit.CLUBS),
            Card(Rank.THREE, Suit.DIAMONDS)
        ]
        
        hand_rank, best_cards = HandEvaluator._find_best_hand(cards)
        self.assertEqual(hand_rank, HandRank.PAIR)
        self.assertEqual(len(best_cards), 5)
    
    def test_high_card(self):
        """Test high card detection."""
        # Ace high
        cards = [
            Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.KING, Suit.DIAMONDS),
            Card(Rank.QUEEN, Suit.CLUBS),
            Card(Rank.NINE, Suit.HEARTS),
            Card(Rank.FIVE, Suit.SPADES),
            Card(Rank.TWO, Suit.CLUBS),
            Card(Rank.THREE, Suit.DIAMONDS)
        ]
        
        hand_rank, best_cards = HandEvaluator._find_best_hand(cards)
        self.assertEqual(hand_rank, HandRank.HIGH_CARD)
        self.assertEqual(len(best_cards), 5)
    
    def test_evaluate_with_community_cards(self):
        """Test evaluation with hole cards and community cards."""
        # Hole cards: A♥ K♥
        hole_cards = [
            Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.KING, Suit.HEARTS)
        ]
        
        # Community cards: Q♥ J♥ 10♥ 2♣ 3♦
        community_cards = [
            Card(Rank.QUEEN, Suit.HEARTS),
            Card(Rank.JACK, Suit.HEARTS),
            Card(Rank.TEN, Suit.HEARTS),
            Card(Rank.TWO, Suit.CLUBS),
            Card(Rank.THREE, Suit.DIAMONDS)
        ]
        
        hand_rank, best_cards = HandEvaluator.evaluate(hole_cards, community_cards)
        self.assertEqual(hand_rank, HandRank.ROYAL_FLUSH)
        self.assertEqual(len(best_cards), 5)


if __name__ == '__main__':
    unittest.main()
