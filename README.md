# Just A Poker Game

A professional Texas Hold'em poker game implementation in Python.

[![Type Checking](https://img.shields.io/badge/type%20checking-mypy-blue)](https://github.com/python/mypy)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## Overview

Just A Poker Game is a comprehensive Texas Hold'em poker game that provides both terminal-based interface and advanced AI opponents. The game is built using object-oriented principles and designed to be modular, maintainable, and easily expandable.

## Features

- **Complete Texas Hold'em rules implementation**
  - Betting rounds (pre-flop, flop, turn, river)
  - Hand evaluation (pair, two pair, straight, flush, etc.)
  - Pot management and distribution
  - Blinds system

- **Player Management**
  - Support for human and AI players
  - Player statistics tracking
  - Persistent player data

- **AI Opponents**
  - Basic AI strategy with configurable parameters
  - Hand strength evaluation
  - Position-based decision making
  - Configurable aggression and bluffing

- **User Interface**
  - Terminal-based colored interface
  - Game state visualization
  - Player action prompts
  - Game statistics display

- **Data Storage**
  - Game history tracking
  - Player statistics persistence
  - Game settings configuration

## Installation

### Prerequisites

- Python 3.8 or higher

### Installation Steps

1. Clone the repository:
   ```
   git clone https://github.com/gianlucamazza/just_a_poker_game.git
   cd just_a_poker_game
   ```

2. Install the package:
   ```
   pip install -e .
   ```

3. Run the game:
   ```
   poker
   ```
   
   Or with command-line options:
   ```
   poker --no-color --small-blind 2 --big-blind 4 --starting-chips 2000
   ```

## Usage

After installation, you can start the game by running the `poker` command. 

### Command-Line Options

The game supports the following command-line options:

- `--help`: Show help message and available options
- `--verbose` or `-v`: Enable verbose logging
- `--no-color`: Disable colored output in the terminal
- `--small-blind AMOUNT`: Set the small blind amount
- `--big-blind AMOUNT`: Set the big blind amount
- `--starting-chips AMOUNT`: Set the starting chips amount for new players

### Main Menu

The main menu provides the following options:

1. **New Game**: Start a new poker game with new or existing players
2. **Load Game**: Continue with previously saved players
3. **Player Statistics**: View statistics for all players
4. **Settings**: Configure game settings
5. **Exit**: Quit the game

### Game Settings

The following settings can be configured:

- **Starting Chips**: The number of chips each player starts with
- **Small Blind**: The small blind amount
- **Big Blind**: The big blind amount
- **Use Colors**: Whether to use colored output in the terminal
- **Animation Speed**: The delay between game actions

### Player Actions

During gameplay, you can perform the following actions:

- **Fold**: Give up your hand and forfeit any bets
- **Check**: Pass the action to the next player (when no bet is required)
- **Call**: Match the current bet
- **Bet**: Place a bet (when no previous bet has been made)
- **Raise**: Increase the current bet
- **All-in**: Bet all your remaining chips

## Project Structure

The project follows a modular structure:

```
just_a_poker_game/
├── just_a_poker_game/        # Main package
│   ├── __init__.py           # Package initialization
│   ├── __main__.py           # Entry point
│   ├── game.py               # Main game class
│   ├── engine/               # Game engine
│   │   ├── card.py           # Card and deck classes
│   │   ├── hand_evaluator.py # Hand evaluation logic
│   │   └── game_state.py     # Game state management
│   ├── player/               # Player management
│   │   └── player.py         # Player class definitions
│   ├── ai/                   # AI components
│   │   └── basic_ai.py       # Basic AI implementation
│   ├── ui/                   # User interface
│   │   └── terminal_ui.py    # Terminal UI implementation
│   └── storage/              # Data persistence
│       └── game_storage.py   # Storage management
├── tests/                    # Unit tests
│   ├── test_card.py          # Card tests
│   └── test_hand_evaluator.py# Hand evaluator tests
├── data/                     # Game data storage
├── logs/                     # Game logs
├── setup.py                  # Package setup script
├── pyproject.toml            # Project configuration
├── mypy.ini                  # Type checking configuration
├── CLAUDE.md                 # Development guidelines
├── requirements.txt          # Package dependencies
└── README.md                 # This file
```

## Extending the Game

### Adding New AI Strategies

You can create new AI players by extending the `Player` class and implementing the `_get_action_impl` method:

```python
from just_a_poker_game.player.player import Player

class AdvancedAIPlayer(Player):
    def _get_action_impl(self, game_state):
        # Implement your advanced strategy
        return action, amount
```

### Adding New UI Implementations

You can create alternative UIs (e.g., a graphical interface) by implementing the necessary display and input methods:

```python
class GraphicalUI:
    def display_table(self, game_state, current_player=None):
        # Implement graphical table display
        pass
        
    def get_player_action(self, player, game_state):
        # Implement graphical action selection
        return action, amount
```

## Development

### Running Tests

To run the tests, use the following command:

```
python -m unittest discover tests
```

To run specific tests:

```
python -m unittest tests.test_card
python -m unittest tests.test_card.TestCard.test_card_creation
```

### Type Checking

The project uses mypy for static type checking. Run type checks with:

```
mypy --config-file mypy.ini just_a_poker_game
```

### Development Guidelines

See the [CLAUDE.md](CLAUDE.md) file for detailed development guidelines including:

- Code style conventions
- Import order and structure
- Type annotation practices
- Documentation standards
- Testing practices

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Texas Hold'em rules and hand rankings
- Terminal color support for various platforms
- Object-oriented design principles for game development
