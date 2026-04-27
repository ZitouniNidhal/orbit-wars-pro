"""
Main Agent - Orbit Wars Pro

Multi-strategy AI agent that combines all strategies
and provides an adaptive approach for the Orbit Wars competition.
"""

from typing import List, Dict, Optional
from agents.utils.game_analyzer import GameAnalyzer, GamePhase
from agents.utils.pathfinding import PathFinder
from agents.utils.combat import CombatResolver
from agents.strategies.greedy import GreedyStrategy
from agents.strategies.aggressive import AggressiveStrategy
from agents.strategies.defensive import DefensiveStrategy
from agents.strategies.hybrid import HybridStrategy


class OrbitWarsPro:
    """
    Professional Orbit Wars agent with multi-strategy support.

    Features:
    - Multiple built-in strategies (greedy, aggressive, defensive, hybrid)
    - Automatic strategy selection based on game state
    - Configurable strategy mode
    - Debug output for analysis
    """

    STRATEGY_GREEDY = 'greedy'
    STRATEGY_AGGRESSIVE = 'aggressive'
    STRATEGY_DEFENSIVE = 'defensive'
    STRATEGY_HYBRID = 'hybrid'
    STRATEGY_ADAPTIVE = 'adaptive'

    def __init__(self, strategy_mode: str = STRATEGY_ADAPTIVE, debug: bool = False):
        """
        Initialize Orbit Wars Pro agent.

        Args:
            strategy_mode: Strategy to use ('greedy', 'aggressive', 'defensive', 'hybrid', 'adaptive')
            debug: Enable debug output
        """
        self.strategy_mode = strategy_mode
        self.debug = debug

        # Initialize strategies
        self.strategies = {
            self.STRATEGY_GREEDY: GreedyStrategy(min_ships_for_attack=15),
            self.STRATEGY_AGGRESSIVE: AggressiveStrategy(min_ships_for_attack=18, attack_ratio=0.65),
            self.STRATEGY_DEFENSIVE: DefensiveStrategy(garrison_target=12, reinforce_threshold=22),
            self.STRATEGY_HYBRID: HybridStrategy(),
        }

        # Track state
        self.current_strategy = strategy_mode
        self.turn_count = 0

    def set_strategy(self, mode: str):
        """
        Set the active strategy mode.

        Args:
            mode: Strategy name
        """
        if mode in self.strategies:
            self.strategy_mode = mode
            self.current_strategy = mode
        elif mode == self.STRATEGY_ADAPTIVE:
            self.current_strategy = mode
        else:
            raise ValueError(f"Unknown strategy: {mode}")

    def act(self, obs: dict) -> List[List]:
        """
        Generate actions based on observation.

        Args:
            obs: Kaggle environment observation

        Returns:
            List of fleet commands [[from_id, angle, ships], ...]
        """
        # Update turn count
        self.turn_count = obs.get('turn', self.turn_count + 1)

        # Analyze game state
        analyzer = GameAnalyzer(obs, obs.get('player', 0))

        # Log debug info
        if self.debug:
            self._debug_log(analyzer)

        # Determine which strategy to use
        if self.strategy_mode == self.STRATEGY_ADAPTIVE:
            self.current_strategy = analyzer.recommend_strategy()
        else:
            self.current_strategy = self.strategy_mode

        # Execute strategy
        strategy = self.strategies.get(
            self.current_strategy,
            self.strategies[self.STRATEGY_HYBRID]
        )

        actions = strategy.get_actions(analyzer)

        # Log actions
        if self.debug and actions:
            print(f"[OrbitWarsPro] Strategy: {self.current_strategy}")
            print(f"[OrbitWarsPro] Actions: {actions}")

        return actions

    def _debug_log(self, analyzer: GameAnalyzer):
        """Log debug information."""
        print(f"\n=== Orbit Wars Pro Debug (Turn {analyzer.turn}) ===")
        print(f"Phase: {analyzer.phase.name}")
        print(f"My planets: {len(analyzer.my_planets)}")
        print(f"Enemy planets: {len(analyzer.enemy_planets)}")
        print(f"Neutral planets: {len(analyzer.neutral_planets)}")
        print(f"My total ships: {analyzer.my_total_ships}")
        print(f"Is losing: {analyzer.is_losing()}")
        print(f"Aggression ratio: {analyzer.get_aggression_ratio():.2f}")
        print(f"Recommended strategy: {analyzer.recommend_strategy()}")

    def get_stats(self, obs: dict) -> Dict:
        """
        Get agent statistics for analysis.

        Args:
            obs: Current observation

        Returns:
            Dictionary with agent stats
        """
        analyzer = GameAnalyzer(obs, obs.get('player', 0))

        return {
            'turn': analyzer.turn,
            'phase': analyzer.phase.name,
            'my_planets': len(analyzer.my_planets),
            'enemy_planets': len(analyzer.enemy_planets),
            'neutral_planets': len(analyzer.neutral_planets),
            'my_ships': analyzer.my_total_ships,
            'my_fleet_ships': analyzer.my_fleet_ships,
            'total_my_ships': analyzer.total_my_ships,
            'is_losing': analyzer.is_losing(),
            'aggression_ratio': analyzer.get_aggression_ratio(),
            'recommended_strategy': analyzer.recommend_strategy(),
            'current_strategy': self.current_strategy,
        }


# Global instance for simple usage
_agent_instance = None


def orbit_wars_agent(obs: dict) -> List[List]:
    """
    Main agent function for Kaggle submission.

    This is the entry point for the Kaggle environment.

    Args:
        obs: Kaggle environment observation

    Returns:
        List of fleet commands
    """
    global _agent_instance

    # Initialize or get agent instance
    if _agent_instance is None:
        _agent_instance = OrbitWarsPro(strategy_mode='adaptive', debug=False)

    return _agent_instance.act(obs)


def reset_agent():
    """Reset the global agent instance."""
    global _agent_instance
    _agent_instance = None


# Alternative entry points for specific strategies
def greedy_agent(obs: dict) -> List[List]:
    """Greedy strategy agent."""
    analyzer = GameAnalyzer(obs, obs.get('player', 0))
    strategy = GreedyStrategy(min_ships_for_attack=15)
    return strategy.get_actions(analyzer)


def aggressive_agent(obs: dict) -> List[List]:
    """Aggressive strategy agent."""
    analyzer = GameAnalyzer(obs, obs.get('player', 0))
    strategy = AggressiveStrategy(min_ships_for_attack=18, attack_ratio=0.65)
    return strategy.get_actions(analyzer)


def defensive_agent(obs: dict) -> List[List]:
    """Defensive strategy agent."""
    analyzer = GameAnalyzer(obs, obs.get('player', 0))
    strategy = DefensiveStrategy(garrison_target=12, reinforce_threshold=22)
    return strategy.get_actions(analyzer)


def hybrid_agent(obs: dict) -> List[List]:
    """Hybrid strategy agent."""
    analyzer = GameAnalyzer(obs, obs.get('player', 0))
    strategy = HybridStrategy()
    return strategy.get_actions(analyzer)


# Demo/test function
if __name__ == '__main__':
    # Example observation for testing
    example_obs = {
        'turn': 1,
        'player': 0,
        'planets': [
            # [id, owner, x, y, radius, ships, production]
            [0, 0, 25, 25, 2.0, 20, 3],  # My home planet
            [1, -1, 40, 30, 1.5, 15, 2],  # Neutral
            [2, -1, 60, 70, 2.0, 25, 4],  # Neutral high production
            [3, 1, 75, 75, 2.0, 18, 3],  # Enemy
        ],
        'fleets': [],
        'angular_velocity': [],
    }

    print("Testing Orbit Wars Pro Agent...")
    print(f"Observation: {example_obs}")

    # Test main agent
    actions = orbit_wars_agent(example_obs)
    print(f"Actions: {actions}")

    # Test with full agent
    agent = OrbitWarsPro(strategy_mode='adaptive', debug=True)
    actions = agent.act(example_obs)
    print(f"\nAgent actions: {actions}")

    # Test different strategies
    print("\n=== Testing Individual Strategies ===")

    print("\nGreedy:")
    print(greedy_agent(example_obs))

    print("\nAggressive:")
    print(aggressive_agent(example_obs))

    print("\nDefensive:")
    print(defensive_agent(example_obs))

    print("\nHybrid:")
    print(hybrid_agent(example_obs))
