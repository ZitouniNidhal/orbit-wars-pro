"""
Combat Resolution Utilities

Handles combat calculations and fleet allocation strategies.
"""

import math
from typing import List, Tuple, Dict
from dataclasses import dataclass
from agents.utils.game_analyzer import Planet, Fleet


@dataclass
class CombatResult:
    """Result of a combat simulation."""
    planet: Planet
    ships_needed: int
    ships_surviving: int
    will_capture: bool
    risk_level: float  # 0.0-1.0


class CombatResolver:
    """
    Combat resolution and fleet allocation calculator.

    Implements the game's combat rules:
    1. All arriving fleets grouped by owner, ships summed
    2. Largest attacking force fights second largest, difference survives
    3. If attacker survives and matches planet owner -> add to garrison
    4. If attacker differs -> fight garrison, excess becomes new garrison
    5. If two attackers tie -> all destroyed
    """

    def __init__(self):
        self.min_surplus_ratio = 1.2  # Need 20% more ships than enemy to be safe
        self.buffer_ships = 5  # Safety buffer for garrison

    def calculate_combat(self, planet: Planet, attacking_ships: int,
                         attacker_owner: int) -> CombatResult:
        """
        Calculate combat outcome for an attack.

        Args:
            planet: Target planet
            attacking_ships: Number of ships in attacking fleet
            attacker_owner: ID of attacking player

        Returns:
            CombatResult with outcome details
        """
        garrison = planet.ships

        # If planet is neutral
        if planet.owner == -1:
            will_capture = attacking_ships > garrison
            ships_needed = garrison + 1
            ships_surviving = attacking_ships - garrison if will_capture else 0
            risk = 0.0 if will_capture else (1 - attacking_ships / (garrison + 1))

            return CombatResult(
                planet=planet,
                ships_needed=ships_needed,
                ships_surviving=max(0, ships_surviving),
                will_capture=will_capture,
                risk_level=risk
            )

        # If attacking own planet (reinforcement)
        if planet.owner == attacker_owner:
            return CombatResult(
                planet=planet,
                ships_needed=0,
                ships_surviving=attacking_ships,
                will_capture=True,
                risk_level=0.0
            )

        # Attacking enemy planet
        # Combat: attacker vs garrison
        if attacking_ships > garrison:
            will_capture = True
            ships_surviving = attacking_ships - garrison
        else:
            will_capture = False
            ships_surviving = 0

        ships_needed = garrison + 1

        # Risk calculation
        if will_capture:
            surplus = attacking_ships / garrison
            risk = max(0, 1 - surplus / self.min_surplus_ratio)
        else:
            risk = 1.0 - (attacking_ships / garrison)

        return CombatResult(
            planet=planet,
            ships_needed=ships_needed,
            ships_surviving=ships_surviving,
            will_capture=will_capture,
            risk_level=min(1.0, max(0.0, risk))
        )

    def optimal_attack_size(self, planet: Planet, available_ships: int,
                            preserve_ratio: float = 0.3) -> int:
        """
        Calculate optimal number of ships to send for attack.

        Args:
            planet: Target planet
            available_ships: Ships available on source planet
            preserve_ratio: Ratio of ships to keep on source (0.0-1.0)

        Returns:
            Optimal number of ships to send
        """
        # Minimum ships needed to capture
        min_needed = planet.ships + 1

        # Maximum we can send while preserving some garrison
        max_send = int(available_ships * (1 - preserve_ratio))

        # Optimal: add safety margin
        optimal = min_needed + self.buffer_ships

        return max(min_needed, min(optimal, max_send))

    def multi_attack_evaluation(self, planet: Planet,
                                 incoming_fleets: List[Fleet],
                                 my_ships: int) -> Dict:
        """
        Evaluate combat when multiple fleets are arriving.

        Args:
            planet: Target planet
            incoming_fleets: All fleets heading to this planet
            my_ships: My ships at this planet (garrison)

        Returns:
            Dictionary with battle evaluation
        """
        # Group fleets by owner
        fleets_by_owner = {}
        for fleet in incoming_fleets:
            owner = fleet.owner
            if owner not in fleets_by_owner:
                fleets_by_owner[owner] = 0
            fleets_by_owner[owner] += fleet.ships

        # Apply game combat rules
        if not fleets_by_owner:
            return {
                'my_ships': my_ships,
                'enemy_ships': 0,
                'will_lose': my_ships <= 0,
                'survivors': my_ships
            }

        # Remove my ships from consideration for fighting
        my_incoming = fleets_by_owner.pop(self.planet.owner if hasattr(self, 'planet') else -1, 0)

        if not fleets_by_owner:
            return {
                'my_ships': my_ships + my_incoming,
                'enemy_ships': 0,
                'will_lose': False,
                'survivors': my_ships + my_incoming
            }

        # Sort attackers by size
        sorted_attackers = sorted(fleets_by_owner.items(), key=lambda x: x[1], reverse=True)

        # Apply combat: largest vs second largest
        if len(sorted_attackers) >= 2:
            largest_owner, largest_ships = sorted_attackers[0]
            second_ships = sorted_attackers[1][1]

            if largest_ships > second_ships:
                fleets_by_owner[largest_owner] = largest_ships - second_ships
            else:
                fleets_by_owner[largest_owner] = 0

        # Now fight garrison
        remaining_attackers = sorted(fleets_by_owner.items(), key=lambda x: x[1], reverse=True)

        current_garrison = my_ships + my_incoming

        for owner, ships in remaining_attackers:
            if ships > current_garrison:
                current_garrison = ships - current_garrison
            else:
                current_garrison = 0
                break

        return {
            'my_ships': my_ships,
            'enemy_ships': sum(fleets_by_owner.values()),
            'will_lose': current_garrison <= 0,
            'survivors': max(0, current_garrison)
        }

    def calculate_defensive_need(self, planet: Planet,
                                 expected_attack: int = 0) -> int:
        """
        Calculate how many ships to keep for defense.

        Args:
            planet: Planet to evaluate
            expected_attack: Expected enemy ships incoming

        Returns:
            Number of ships to keep for defense
        """
        base_defense = planet.ships + expected_attack + self.buffer_ships
        return max(planet.ships, base_defense)

    def evaluate_attack_risk(self, source: Planet, target: Planet,
                             ships_to_send: int) -> float:
        """
        Evaluate risk of an attack.

        Returns:
            Risk score from 0.0 (safe) to 1.0 (very risky)
        """
        combat = self.calculate_combat(target, ships_to_send, source.owner)

        # Risk factors
        distance_factor = min(source.distance_to(target) / 100, 1.0) * 0.2

        # Time factor - longer travel = more risk of enemy reinforcement
        travel_time = source.distance_to(target) / 5  # Rough estimate
        time_factor = min(travel_time / 50, 0.3)

        # Combat risk
        combat_risk = combat.risk_level * 0.5

        total_risk = distance_factor + time_factor + combat_risk

        return min(1.0, total_risk)
