"""
Aggressive Strategy

Prioritizes attacking enemy planets and eliminating opponents.
Best against defensive or expanding opponents.
"""

import math
from typing import List, Tuple, Optional
from agents.utils.game_analyzer import GameAnalyzer, Planet, Fleet, GamePhase
from agents.utils.pathfinding import PathFinder
from agents.utils.combat import CombatResolver


class AggressiveStrategy:
    """
    Aggressive attack strategy focusing on enemy elimination.

    This strategy prioritizes attacking weak enemy planets
    and aims to quickly eliminate competition.
    """

    def __init__(self, min_ships_for_attack: int = 20, attack_ratio: float = 0.7):
        """
        Initialize aggressive strategy.

        Args:
            min_ships_for_attack: Minimum ships to consider for attack
            attack_ratio: Ratio of ships to send on attack (0.0-1.0)
        """
        self.min_ships_for_attack = min_ships_for_attack
        self.attack_ratio = attack_ratio
        self.combat = CombatResolver()

    def get_actions(self, analyzer: GameAnalyzer) -> List[List]:
        """
        Generate actions for aggressive strategy.

        Args:
            analyzer: Game state analyzer

        Returns:
            List of [from_planet_id, angle, num_ships] commands
        """
        actions = []
        pathfinder = PathFinder(analyzer.planets)

        # Get planets with surplus ships
        expandable = analyzer.get_expandable_planets(self.min_ships_for_attack)

        # Track commanded planets
        commanded = set()

        # Priority 1: Attack weakest enemy planets
        for source in expandable:
            if source.id in commanded:
                continue

            weakest_enemy = analyzer.get_weakest_enemy_planet()
            if not weakest_enemy:
                continue

            # Check if we can win
            combat = self.combat.calculate_combat(
                weakest_enemy, source.ships - 10, analyzer.player
            )

            if combat.will_capture and combat.risk_level < 0.3:
                ships_to_send = int((source.ships - 10) * self.attack_ratio)
                ships_to_send = max(ships_to_send, combat.ships_needed)

                if ships_to_send >= self.min_ships_for_attack:
                    angle = pathfinder.find_safe_launch_angle(source, weakest_enemy)[0]
                    actions.append([source.id, angle, ships_to_send])
                    commanded.add(source.id)

        # Priority 2: Attack any reachable enemy
        if len(actions) < 2:
            for source in expandable:
                if source.id in commanded:
                    continue

                for enemy in analyzer.enemy_planets:
                    dist = source.distance_to(enemy)
                    if dist > 60:  # Too far
                        continue

                    # Check sun collision
                    angle = pathfinder.calculate_angle(source.x, source.y, enemy.x, enemy.y)
                    if pathfinder._check_sun_collision(source.x, source.y, angle, dist):
                        continue

                    # Calculate if attack is viable
                    ships_available = source.ships - 8
                    combat = self.combat.calculate_combat(
                        enemy, ships_available, analyzer.player
                    )

                    if combat.will_capture:
                        ships_to_send = max(
                            combat.ships_needed,
                            int(ships_available * self.attack_ratio)
                        )

                        if ships_to_send >= self.min_ships_for_attack:
                            safe_angle = pathfinder.find_safe_launch_angle(source, enemy)[0]
                            actions.append([source.id, safe_angle, ships_to_send])
                            commanded.add(source.id)
                            break

        # Priority 3: Support ongoing attacks
        if len(actions) < 3 and expandable:
            # Find nearest friendly planet to reinforce
            strongest = analyzer.get_strongest_home_planet()
            if strongest and strongest.id not in commanded:
                # Find closest enemy
                closest_enemy = None
                min_dist = float('inf')
                for enemy in analyzer.enemy_planets:
                    dist = strongest.distance_to(enemy)
                    if dist < min_dist:
                        min_dist = dist
                        closest_enemy = enemy

                if closest_enemy:
                    ships = int((strongest.ships - 15) * 0.5)
                    if ships >= 15:
                        angle = pathfinder.calculate_angle(
                            strongest.x, strongest.y, closest_enemy.x, closest_enemy.y
                        )
                        actions.append([strongest.id, angle, ships])
                        commanded.add(strongest.id)

        return actions


def aggressive_agent(obs: dict) -> List[List]:
    """
    Standalone aggressive agent function.

    Args:
        obs: Kaggle environment observation

    Returns:
        List of fleet commands
    """
    analyzer = GameAnalyzer(obs, obs.get('player', 0))
    strategy = AggressiveStrategy()

    # Adjust based on game phase
    if analyzer.phase == GamePhase.LATE:
        strategy = AggressiveStrategy(min_ships_for_attack=15, attack_ratio=0.8)
    elif analyzer.phase == GamePhase.MID:
        strategy = AggressiveStrategy(min_ships_for_attack=18, attack_ratio=0.7)

    return strategy.get_actions(analyzer)
