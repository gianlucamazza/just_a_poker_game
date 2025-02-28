# Just A Poker Game - Development Guidelines

## Build & Test Commands
- Install for development: `pip install -e .`
- Run the game: `poker` or `python -m just_a_poker_game`
- Run all tests: `python -m unittest discover tests`
- Run single test: `python -m unittest tests.test_card.TestCard.test_card_creation`
- Run single test file: `python -m unittest tests.test_card`
- Run type checks: `mypy --config-file mypy.ini just_a_poker_game`

## Code Style Guidelines
- **Imports**: Standard lib first, third-party next, project-specific last (alphabetized within groups)
- **Naming**: PascalCase for classes, snake_case for functions/methods, UPPER_SNAKE_CASE for constants
- **Types**: Use type hints for all function parameters and return values, import from typing module
- **Docstrings**: Triple double quotes, module purpose, class description with Attributes, method description with Args/Returns
- **Error Handling**: Use exceptions for invalid states (ValueError), validate parameters before use
- **OOP**: Use abstract base classes for interfaces, private methods prefixed with underscore (_method_name)
- **Modules**: Keep modules focused on a single responsibility, group related functionality
- **Testing**: Unit tests for all classes, use descriptive test method names (test_what_happens_when_condition)
- **Null Checks**: Always check for None before accessing attributes of optional objects

## Type Checking Notes
- Game state operations should always check for None: `if not self.game_state: return`
- Use Optional[T] for parameters that can be None
- Cast types when needed for settings: `int(self.settings['small_blind'])`
- Some modules have special type checking exceptions in mypy.ini