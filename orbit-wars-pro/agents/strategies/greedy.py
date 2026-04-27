"""
Greedy Strategy

Prioritizes neutral planet capture and resource accumulation.
Best against passive opponents.
"""

import math
from typing import List, Tuple, Optional
from agents.utils.game_analyzer import GameAnalyzer, Planet, GamePhase
from agents.utils.pathfinding import PathFinder
from agents.utils.combat import CombatResolver


class GreedyStrategy:
    """
    Greedy expansion strategy focusing on capturing neutrals.

    This strategy is most effective in early game and against
    passive opponents who don't contest neutral planets.
    """

    def __init__(self, min_ships_for_attack: int = 15):
        """
        Initialize greedy strategy.

        Args:
            min_ships_for_attack: Minimum ships to consider for attack
        """
        self.min_ships_for_attack = min_ships_for_attack
        self.combat = CombatResolver()

    def get_actions(self, analyzer: GameAnalyzer) -> List[List]:
        """
        Generate actions for greedy strategy.

        Args:
            analyzer: Game state analyzer

        Returns:
            List of [from_planet_id, angle, num_ships] commands
        """
        actions = []
        pathfinder = PathFinder(analyzer.planets)

        # Get expandable planets sorted by production
        expandable = analyzer.get_expandable_planets(self.min_ships_for_attack)

        # Track which planets we've already commanded
        commanded_planets = set()

        for source in expandable:
            if source.id in commanded_planets:
                continue

            # Find best neutral target
            best_target = None
            best_score = -1

            for neutral in analyzer.neutral_planets:
                # Calculate score: production / distance
                dist = source.distance_to(neutral)
                if dist < 1:
                    continue

                # Check if path is safe (no sun collision)
                angle = pathfinder.calculate_angle(source.x, source.y, neutral.x, neutral.y)
                if pathfinder._check_sun_collision(source.x, source.y, angle, dist):
                    continue

                # Score based on production value and distance
                score = neutral.production * 10 / dist

                if score > best_score:
                    best_score = score
                    best_target = neutral

            if best_target and best_score > 0:
                # Calculate ships to send
                ships_available = source.ships - 10  # Keep 10 as garrison
                if ships_available < self.min_ships_for_attack:
                    continue

                # Ships needed to capture
                combat = self.combat.calculate_combat(
                    best_target, ships_available, analyzer.player
                )
                ships_to_send = max(combat.ships_needed, min(ships_available, 50))

                # Only send if we have enough
                if ships_to_send >= self.min_ships_for_attack:
                    angle = pathfinder.find_safe_launch_angle(source, best_target)[0]

                    actions.append([source.id, angle, ships_to_send])
                    commanded_planets.add(source.id)

        # If we have no neutral targets, reinforce existing planets
        if not actions and expandable:
            strongest = analyzer.get_strongest_home_planet()
            if strongest and strongest.ships > 30:
                # Find weakest owned planet
                weakest = min(analyzer.my_planets, key=lambda p: p.ships)
                if weakest.id != strongest.id:
                    ships_to_send = min(20, strongest.ships - 15)
                    angle = pathfinder.calculate_angle(
                        strongest.x, strongest.y, weakest.x, weakest.y
                    )
                    actions.append([strongest.id, angle, ships_to_send])

        return actions


def greedy_agent(obs: dict) -> List[List]:
    """
    Standalone greedy agent function.

    Args:
        obs: Kaggle environment observation

    Returns:
        List of fleet commands
    """
    analyzer = GameAnalyzer(obs, obs.get('player', 0))
    strategy = GreedyStrategy()

    # Apply early game bias
    if analyzer.phase == GamePhase.EARLY:
        strategy = GreedyStrategy(min_ships_for_attack=12)
    elif analyzer.phase == GamePhase.MID:
        strategy = GreedyStrategy(min_ships_for_attack=18)

    return strategy.get_actions(analyzer)
