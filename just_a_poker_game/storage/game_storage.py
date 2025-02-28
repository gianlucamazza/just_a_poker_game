"""
Storage module for poker game data.

This module handles saving and loading game data, player statistics,
and game history.
"""
import os
import json
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from just_a_poker_game.player.player import Player, HumanPlayer
from just_a_poker_game.ai.basic_ai import BasicAIPlayer


logger = logging.getLogger(__name__)


class GameStorage:
    """
    Handles storage and retrieval of game data.
    
    Attributes:
        storage_dir (str): Directory for storing game data.
        players_file (str): File path for player data.
        history_file (str): File path for game history.
        settings_file (str): File path for game settings.
    """
    
    def __init__(self, storage_dir: str = None):
        """
        Initialize the storage system.
        
        Args:
            storage_dir: Directory for storing data (default: ./data)
        """
        if storage_dir is None:
            # Use default data directory
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            storage_dir = os.path.join(base_dir, 'data')
        
        self.storage_dir = storage_dir
        self.players_file = os.path.join(storage_dir, 'players.json')
        self.history_file = os.path.join(storage_dir, 'history.json')
        self.settings_file = os.path.join(storage_dir, 'settings.json')
        
        # Ensure the storage directory exists
        os.makedirs(storage_dir, exist_ok=True)
    
    def save_players(self, players: List[Player]) -> bool:
        """
        Save player data.
        
        Args:
            players: List of players to save.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            player_data = [player.to_dict() for player in players]
            
            with open(self.players_file, 'w') as f:
                json.dump({'players': player_data}, f, indent=2)
            
            logger.info(f"Saved {len(players)} players to {self.players_file}")
            return True
        
        except Exception as e:
            logger.error(f"Error saving players: {e}")
            return False
    
    def load_players(self) -> List[Player]:
        """
        Load player data.
        
        Returns:
            List of Player objects.
        """
        try:
            if not os.path.exists(self.players_file):
                logger.info(f"No players file found at {self.players_file}")
                return []
            
            with open(self.players_file, 'r') as f:
                data = json.load(f)
            
            players = []
            for player_data in data.get('players', []):
                player_type = player_data.get('type', 'human')
                
                if player_type == 'ai':
                    player = BasicAIPlayer.from_dict(player_data)
                else:
                    player = HumanPlayer.from_dict(player_data)
                
                players.append(player)
            
            logger.info(f"Loaded {len(players)} players from {self.players_file}")
            return players
        
        except Exception as e:
            logger.error(f"Error loading players: {e}")
            return []
    
    def save_game_history(self, history_entry: Dict[str, Any]) -> bool:
        """
        Save a game history entry.
        
        Args:
            history_entry: Game history data to save.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Add timestamp if not present
            if 'timestamp' not in history_entry:
                history_entry['timestamp'] = datetime.now().isoformat()
            
            # Load existing history
            history = self._load_history()
            
            # Add new entry
            history.append(history_entry)
            
            # Save updated history
            with open(self.history_file, 'w') as f:
                json.dump({'history': history}, f, indent=2)
            
            logger.info(f"Saved game history entry to {self.history_file}")
            return True
        
        except Exception as e:
            logger.error(f"Error saving game history: {e}")
            return False
    
    def get_game_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        Get game history entries.
        
        Args:
            limit: Maximum number of entries to retrieve (newest first).
            
        Returns:
            List of game history entries.
        """
        history = self._load_history()
        
        # Sort by timestamp (newest first)
        history.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Apply limit if specified
        if limit is not None and limit > 0:
            history = history[:limit]
        
        return history
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """
        Load game history data.
        
        Returns:
            List of game history entries.
        """
        try:
            if not os.path.exists(self.history_file):
                return []
            
            with open(self.history_file, 'r') as f:
                data = json.load(f)
            
            return data.get('history', [])
        
        except Exception as e:
            logger.error(f"Error loading game history: {e}")
            return []
    
    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """
        Save game settings.
        
        Args:
            settings: Game settings to save.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            logger.info(f"Saved game settings to {self.settings_file}")
            return True
        
        except Exception as e:
            logger.error(f"Error saving game settings: {e}")
            return False
    
    def load_settings(self) -> Dict[str, Any]:
        """
        Load game settings.
        
        Returns:
            Game settings.
        """
        try:
            if not os.path.exists(self.settings_file):
                logger.info(f"No settings file found at {self.settings_file}")
                return {}
            
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
            
            logger.info(f"Loaded game settings from {self.settings_file}")
            return settings
        
        except Exception as e:
            logger.error(f"Error loading game settings: {e}")
            return {}
