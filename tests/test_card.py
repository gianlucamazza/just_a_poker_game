"""
Tests for the card module.
"""
import unittest
from just_a_poker_game.engine.card import Card, Rank, Suit, Deck


class TestCard(unittest.TestCase):
    """Test cases for Card class."""
    
    def test_card_creation(self):
        """Test card creation and attributes."""
        card = Card(Rank.ACE, Suit.SPADES)
        self.assertEqual(card.rank, Rank.ACE)
        self.assertEqual(card.suit, Suit.SPADES)
    
    def test_card_equality(self):
        """Test card equality."""
        card1 = Card(Rank.ACE, Suit.SPADES)
        card2 = Card(Rank.ACE, Suit.SPADES)
        card3 = Card(Rank.KING, Suit.SPADES)
        
        self.assertEqual(card1, card2)
        self.assertNotEqual(card1, card3)
    
    def test_card_comparison(self):
        """Test card comparison."""
        ace = Card(Rank.ACE, Suit.HEARTS)
        king = Card(Rank.KING, Suit.HEARTS)
        queen = Card(Rank.QUEEN, Suit.HEARTS)
        
        self.assertTrue(king < ace)
        self.assertTrue(queen < king)
        self.assertTrue(ace > king)
    
    def test_card_string_representation(self):
        """Test card string representation."""
        card = Card(Rank.ACE, Suit.HEARTS)
        self.assertIn("A", str(card))
        self.assertIn("♥", str(card))


class TestDeck(unittest.TestCase):
    """Test cases for Deck class."""
    
    def test_deck_creation(self):
        """Test deck creation and size."""
        deck = Deck()
        self.assertEqual(len(deck), 52)
    
    def test_deck_shuffle(self):
        """Test deck shuffling."""
        deck1 = Deck()
        deck2 = Deck()
        
        # Make a copy of the cards
        cards1 = deck1.cards.copy()
        
        # Shuffle one deck
        deck2.shuffle()
        
        # Check that the order is likely different
        # (there's a tiny chance they could be the same)
        self.assertNotEqual(cards1, deck2.cards)
    
    def test_deal_card(self):
        """Test dealing a card."""
        deck = Deck()
        initial_size = len(deck)
        
        card = deck.deal()
        
        self.assertIsInstance(card, Card)
        self.assertEqual(len(deck), initial_size - 1)
    
    def test_deal_multiple_cards(self):
        """Test dealing multiple cards."""
        deck = Deck()
        initial_size = len(deck)
        
        cards = deck.deal_multiple(5)
        
        self.assertEqual(len(cards), 5)
        self.assertEqual(len(deck), initial_size - 5)
    
    def test_empty_deck(self):
        """Test dealing from an empty deck."""
        deck = Deck()
        
        # Deal all cards
        while len(deck) > 0:
            deck.deal()
        
        # Try to deal from empty deck
        with self.assertRaises(IndexError):
            deck.deal()


if __name__ == '__main__':
    unittest.main()
