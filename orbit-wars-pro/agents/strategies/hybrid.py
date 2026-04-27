"""
Hybrid Strategy

Combines multiple strategies based on game state.
Adaptive and balanced approach for general use.
"""

import math
from typing import List, Tuple, Optional, Dict
from agents.utils.game_analyzer import GameAnalyzer, Planet, Fleet, GamePhase
from agents.utils.pathfinding import PathFinder
from agents.utils.combat import CombatResolver
from agents.strategies.greedy import GreedyStrategy
from agents.strategies.aggressive import AggressiveStrategy
from agents.strategies.defensive import DefensiveStrategy


class HybridStrategy:
    """
    Hybrid strategy combining greedy, aggressive, and defensive approaches.

    Automatically adjusts priorities based on game state:
    - Early game: Focus on neutral capture (greedy)
    - Mid game: Balance offense and defense (hybrid)
    - Late game: Prioritize wins (aggressive)
    """

    def __init__(self):
        """Initialize hybrid strategy with sub-strategies."""
        self.greedy = GreedyStrategy(min_ships_for_attack=15)
        self.aggressive = AggressiveStrategy(min_ships_for_attack=20, attack_ratio=0.6)
        self.defensive = DefensiveStrategy(garrison_target=12, reinforce_threshold=22)

        # State tracking
        self.last_switch_turn = 0
        self.current_mode = 'balanced'

    def get_actions(self, analyzer: GameAnalyzer) -> List[List]:
        """
        Generate actions using hybrid approach.

        Args:
            analyzer: Game state analyzer

        Returns:
            List of [from_planet_id, angle, num_ships] commands
        """
        actions = []
        pathfinder = PathFinder(analyzer.planets)

        # Determine game situation
        phase = analyzer.phase
        is_losing = analyzer.is_losing()
        aggression_ratio = analyzer.get_aggression_ratio()
        num_players = analyzer.count_total_players()

        # Decide primary mode
        if phase == GamePhase.EARLY:
            primary_mode = 'greedy'
        elif phase == GamePhase.MID:
            if is_losing and aggression_ratio > 1.3:
                primary_mode = 'defensive'
            elif len(analyzer.my_planets) < 2:
                primary_mode = 'greedy'
            else:
                primary_mode = 'balanced'
        else:  # LATE
            if is_losing:
                primary_mode = 'aggressive'
            else:
                primary_mode = 'balanced'

        # Execute based on primary mode
        if primary_mode == 'greedy':
            actions = self._greedy_centric(analyzer, pathfinder)
        elif primary_mode == 'aggressive':
            actions = self._aggressive_centric(analyzer, pathfinder)
        elif primary_mode == 'defensive':
            actions = self._defensive_centric(analyzer, pathfinder)
        else:  # balanced
            actions = self._balanced(analyzer, pathfinder)

        return actions

    def _greedy_centric(self, analyzer: GameAnalyzer, pathfinder: PathFinder) -> List[List]:
        """Greedy-focused with some defense."""
        actions = []

        # First, get greedy actions
        greedy_actions = self.greedy.get_actions(analyzer)
        actions.extend(greedy_actions[:2])  # Limit greedy actions

        # If no greedy actions, do defensive
        if not actions:
            actions = self.defensive.get_actions(analyzer)

        return actions

    def _aggressive_centric(self, analyzer: GameAnalyzer, pathfinder: PathFinder) -> List[List]:
        """Aggressive-focused with reinforcement."""
        actions = []

        # Get aggressive actions first
        aggressive_actions = self.aggressive.get_actions(analyzer)
        actions.extend(aggressive_actions[:2])

        # Fill remaining capacity with greedy
        if len(actions) < 2:
            greedy_actions = self.greedy.get_actions(analyzer)
            for action in greedy_actions:
                if len(actions) >= 3:
                    break
                # Check if not duplicating
                if not any(a[0] == action[0] for a in actions):
                    actions.append(action)

        return actions

    def _defensive_centric(self, analyzer: GameAnalyzer, pathfinder: PathFinder) -> List[List]:
        """Defensive-focused with opportunistic attacks."""
        actions = []

        # Get defensive actions first
        defensive_actions = self.defensive.get_actions(analyzer)
        actions.extend(defensive_actions[:2])

        # Check for easy kills
        easy_kills = self._find_easy_kills(analyzer, pathfinder)
        for kill in easy_kills:
            if len(actions) >= 3:
                break
            if not any(a[0] == kill[0] for a in actions):
                actions.append(kill)

        return actions

    def _balanced(self, analyzer: GameAnalyzer, pathfinder: PathFinder) -> List[List]:
        """Balanced approach mixing all strategies."""
        actions = []
        action_sources = set()

        # Priority 1: Easy neutral captures
        greedy_actions = self.greedy.get_actions(analyzer)
        for action in greedy_actions[:1]:
            actions.append(action)
            action_sources.add(action[0])

        # Priority 2: Weak enemy targets
        easy_kills = self._find_easy_kills(analyzer, pathfinder)
        for kill in easy_kills:
            if len(actions) >= 2:
                break
            if kill[0] not in action_sources:
                actions.append(kill)
                action_sources.add(kill[0])

        # Priority 3: Reinforce if needed
        if len(actions) < 2:
            defensive_actions = self.defensive.get_actions(analyzer)
            for action in defensive_actions[:1]:
                if action[0] not in action_sources:
                    actions.append(action)
                    action_sources.add(action[0])

        return actions

    def _find_easy_kills(self, analyzer: GameAnalyzer,
                         pathfinder: PathFinder) -> List[List]:
        """Find weak enemy planets that can be easily captured."""
        easy_kills = []
        combat = CombatResolver()

        for source in analyzer.get_expandable_planets(15):
            for enemy in analyzer.enemy_planets:
                dist = source.distance_to(enemy)

                # Only nearby targets
                if dist > 50:
                    continue

                # Check sun
                angle = pathfinder.calculate_angle(source.x, source.y, enemy.x, enemy.y)
                if pathfinder._check_sun_collision(source.x, source.y, angle, dist):
                    continue

                # Check if we can win
                ships_available = source.ships - 10
                combat_result = combat.calculate_combat(enemy, ships_available, analyzer.player)

                # Easy kill: low risk and will capture
                if combat_result.will_capture and combat_result.risk_level < 0.2:
                    ships_to_send = max(combat_result.ships_needed, int(ships_available * 0.6))
                    safe_angle = pathfinder.find_safe_launch_angle(source, enemy)[0]
                    easy_kills.append([source.id, safe_angle, ships_to_send])
                    break

        return easy_kills


def hybrid_agent(obs: dict) -> List[List]:
    """
    Standalone hybrid agent function.

    Args:
        obs: Kaggle environment observation

    Returns:
        List of fleet commands
    """
    analyzer = GameAnalyzer(obs, obs.get('player', 0))
    strategy = HybridStrategy()
    return strategy.get_actions(analyzer)
