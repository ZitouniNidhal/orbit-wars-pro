"""
Defensive Strategy

Focuses on consolidating positions and defending against attacks.
Best against aggressive opponents.
"""

import math
from typing import List, Tuple, Optional
from agents.utils.game_analyzer import GameAnalyzer, Planet, Fleet, GamePhase
from agents.utils.pathfinding import PathFinder
from agents.utils.combat import CombatResolver


class DefensiveStrategy:
    """
    Defensive consolidation strategy.

    This strategy focuses on strengthening positions,
    reinforcing vulnerable planets, and waiting for
    safe opportunities rather than taking risks.
    """

    def __init__(self, garrison_target: int = 15, reinforce_threshold: int = 25):
        """
        Initialize defensive strategy.

        Args:
            garrison_target: Target ships to keep on each planet
            reinforce_threshold: Send reinforcements when planet has this many ships
        """
        self.garrison_target = garrison_target
        self.reinforce_threshold = reinforce_threshold
        self.combat = CombatResolver()

    def get_actions(self, analyzer: GameAnalyzer) -> List[List]:
        """
        Generate actions for defensive strategy.

        Args:
            analyzer: Game state analyzer

        Returns:
            List of [from_planet_id, angle, num_ships] commands
        """
        actions = []
        pathfinder = PathFinder(analyzer.planets)

        # Identify vulnerable planets
        vulnerable = []
        well_defended = []

        for planet in analyzer.my_planets:
            if planet.ships < self.garrison_target:
                vulnerable.append(planet)
            else:
                well_defended.append(planet)

        # Priority 1: Reinforce vulnerable planets
        for vulnerable_planet in vulnerable:
            # Find strongest planet to reinforce from
            best_reinforcer = None
            max_ships = 0

            for planet in well_defended:
                if planet.ships > self.garrison_target + 10:
                    if planet.ships > max_ships:
                        max_ships = planet.ships
                        best_reinforcer = planet

            if best_reinforcer:
                ships_needed = self.garrison_target - vulnerable_planet.ships + 5
                ships_to_send = min(ships_needed, best_reinforcer.ships - self.garrison_target)

                if ships_to_send >= 8:
                    angle = pathfinder.calculate_angle(
                        best_reinforcer.x, best_reinforcer.y,
                        vulnerable_planet.x, vulnerable_planet.y
                    )
                    actions.append([best_reinforcer.id, angle, ships_to_send])

                    # Update well_defended for tracking
                    well_defended = [p for p in well_defended if p.id != best_reinforcer.id]
                    if best_reinforcer.ships - ships_to_send >= self.garrison_target:
                        well_defended.append(
                            Planet(
                                best_reinforcer.id, best_reinforcer.owner,
                                best_reinforcer.x, best_reinforcer.y,
                                best_reinforcer.radius,
                                best_reinforcer.ships - ships_to_send,
                                best_reinforcer.production
                            )
                        )

        # Priority 2: Capture nearby neutrals if well defended
        if len(actions) < 2:
            for planet in well_defended:
                if planet.ships < self.reinforce_threshold:
                    continue

                # Find closest neutral
                best_target = None
                best_score = -1

                for neutral in analyzer.neutral_planets:
                    dist = planet.distance_to(neutral)
                    if dist > 40:  # Not too far
                        continue

                    # Check sun collision
                    angle = pathfinder.calculate_angle(planet.x, planet.y, neutral.x, neutral.y)
                    if pathfinder._check_sun_collision(planet.x, planet.y, angle, dist):
                        continue

                    score = neutral.production * 10 / max(dist, 1)
                    if score > best_score:
                        best_score = score
                        best_target = neutral

                if best_target:
                    ships_available = planet.ships - self.garrison_target
                    combat = self.combat.calculate_combat(
                        best_target, ships_available, analyzer.player
                    )

                    ships_to_send = max(combat.ships_needed, min(20, ships_available))
                    if ships_to_send >= 10:
                        angle = pathfinder.find_safe_launch_angle(planet, best_target)[0]
                        actions.append([planet.id, angle, ships_to_send])
                        well_defended = [p for p in well_defended if p.id != planet.id]
                        break

        # Priority 3: Concentrate forces on strongest planet
        if not actions:
            strongest = analyzer.get_strongest_home_planet()
            if strongest and strongest.ships > self.reinforce_threshold + 20:
                for planet in well_defended:
                    if planet.id == strongest.id:
                        continue

                    ships_to_move = planet.ships - 10
                    if ships_to_move >= 10:
                        angle = pathfinder.calculate_angle(
                            planet.x, planet.y, strongest.x, strongest.y
                        )
                        actions.append([planet.id, angle, ships_to_move])

        return actions


def defensive_agent(obs: dict) -> List[List]:
    """
    Standalone defensive agent function.

    Args:
        obs: Kaggle environment observation

    Returns:
        List of fleet commands
    """
    analyzer = GameAnalyzer(obs, obs.get('player', 0))
    strategy = DefensiveStrategy()

    # Adjust based on game phase and situation
    if analyzer.is_losing():
        strategy = DefensiveStrategy(garrison_target=20, reinforce_threshold=30)
    elif analyzer.phase == GamePhase.MID:
        strategy = DefensiveStrategy(garrison_target=15, reinforce_threshold=25)

    return strategy.get_actions(analyzer)
