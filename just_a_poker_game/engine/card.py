"""
Card handling module for poker game.
"""
from enum import Enum, auto
from typing import List
import random


class Suit(Enum):
    """Card suit enumeration."""
    HEARTS = auto()
    DIAMONDS = auto()
    CLUBS = auto()
    SPADES = auto()

    def __str__(self) -> str:
        return self.name.capitalize()
    
    @property
    def symbol(self) -> str:
        """Return the symbol representation of the suit."""
        symbols = {
            Suit.HEARTS: "♥",
            Suit.DIAMONDS: "♦",
            Suit.CLUBS: "♣",
            Suit.SPADES: "♠"
        }
        return symbols[self]


class Rank(Enum):
    """Card rank enumeration."""
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

    def __str__(self) -> str:
        if self.value <= 10:
            return str(self.value)
        name_map = {
            Rank.JACK: "J",
            Rank.QUEEN: "Q",
            Rank.KING: "K",
            Rank.ACE: "A"
        }
        return name_map[self]


class Card:
    """
    Representation of a playing card.
    
    Attributes:
        rank (Rank): The rank of the card.
        suit (Suit): The suit of the card.
    """
    
    def __init__(self, rank: Rank, suit: Suit):
        """Initialize a card with a rank and suit."""
        self.rank = rank
        self.suit = suit
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Card):
            return False
        return self.rank == other.rank and self.suit == other.suit
    
    def __lt__(self, other) -> bool:
        if not isinstance(other, Card):
            return NotImplemented
        return self.rank.value < other.rank.value
    
    def __hash__(self) -> int:
        return hash((self.rank, self.suit))
    
    def __str__(self) -> str:
        return f"{self.rank}{self.suit.symbol}"
    
    def __repr__(self) -> str:
        return f"Card({self.rank}, {self.suit})"


class Deck:
    """
    A deck of playing cards.
    
    Attributes:
        cards (List[Card]): List of cards in the deck.
    """
    
    def __init__(self):
        """Initialize a standard 52-card deck."""
        self.cards: List[Card] = []
        self.reset()
    
    def reset(self):
        """Reset the deck to a full, unshuffled state."""
        self.cards = [Card(rank, suit) for suit in Suit for rank in Rank]
    
    def shuffle(self):
        """Shuffle the deck."""
        random.shuffle(self.cards)
    
    def deal(self) -> Card:
        """
        Deal a card from the top of the deck.
        
        Returns:
            Card: The dealt card.
            
        Raises:
            IndexError: If the deck is empty.
        """
        if not self.cards:
            raise IndexError("Cannot deal from an empty deck")
        return self.cards.pop()
    
    def deal_multiple(self, count: int) -> List[Card]:
        """
        Deal multiple cards from the deck.
        
        Args:
            count: Number of cards to deal.
            
        Returns:
            List[Card]: List of dealt cards.
            
        Raises:
            IndexError: If not enough cards are in the deck.
        """
        if len(self.cards) < count:
            raise IndexError(f"Cannot deal {count} cards, only {len(self.cards)} remaining")
        
        return [self.deal() for _ in range(count)]
    
    def __len__(self) -> int:
        return len(self.cards)
    
    def __str__(self) -> str:
        return f"Deck with {len(self.cards)} cards"
