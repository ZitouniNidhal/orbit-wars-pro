"""
Game State Analysis Utilities

Provides comprehensive game state analysis including:
- Planet scoring and valuation
- Fleet trajectory calculations
- Game phase detection
- Threat assessment
"""

import math
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class GamePhase(Enum):
    """Game phases based on turn count."""
    EARLY = 1      # Turns 1-100
    MID = 2        # Turns 101-300
    LATE = 3       # Turns 301-500


class PlanetType(Enum):
    """Planet classification."""
    HOME = 'home'
    NEUTRAL = 'neutral'
    ENEMY = 'enemy'
    FRIENDLY = 'friendly'
    COMET = 'comet'


@dataclass
class Planet:
    """Planet data structure."""
    id: int
    owner: int
    x: float
    y: float
    radius: float
    ships: int
    production: int
    angular_velocity: float = 0.0
    angle: float = 0.0

    def distance_to(self, other: 'Planet') -> float:
        """Calculate Euclidean distance to another planet."""
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def angle_to(self, other: 'Planet') -> float:
        """Calculate angle to another planet in radians."""
        return math.atan2(other.y - self.y, other.x - self.x)

    @property
    def planet_type(self) -> PlanetType:
        """Classify planet ownership type."""
        if self.production == 1 and self.radius <= 1.5:
            return PlanetType.COMET
        return PlanetType.NEUTRAL if self.owner == -1 else PlanetType.HOME

    def score_value(self, game_phase: GamePhase = GamePhase.MID) -> float:
        """
        Calculate strategic value score for this planet.

        Higher score = higher priority target.
        """
        base_value = self.production * 10

        # Distance penalty (closer is better)
        distance_factor = max(0, 1 - (self.distance_to(Planet(0, 50, 50, 0, 0, 0, 0)) / 100))

        # Ships factor (fewer ships = easier target)
        if self.owner == -1:
            ship_factor = max(0, 1 - (self.ships / 100))
        else:
            ship_factor = min(1, self.ships / 50)

        # Phase adjustments
        if game_phase == GamePhase.EARLY:
            # Early game: prioritize production and neutrals
            value = base_value * 1.5 + self.production * 5
            value *= (1 + distance_factor)
        elif game_phase == GamePhase.MID:
            # Mid game: balanced evaluation
            value = base_value * 1.2
            if self.owner != -1:
                value *= 1.3  # Combat planets are more valuable
        else:  # LATE
            # Late game: prioritize quick wins
            value = base_value
            if self.ships < 30:
                value *= 2.0  # Low-ship targets are priority

        return value * (1 - ship_factor * 0.3)


@dataclass
class Fleet:
    """Fleet data structure."""
    id: int
    owner: int
    x: float
    y: float
    angle: float
    from_planet_id: int
    ships: int

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'owner': self.owner,
            'x': self.x,
            'y': self.y,
            'angle': self.angle,
            'from_planet_id': self.from_planet_id,
            'ships': self.ships
        }


class GameAnalyzer:
    """
    Comprehensive game state analyzer.

    Provides utilities for understanding the current game state
    and calculating strategic values.
    """

    # Constants from competition rules
    BOARD_SIZE = 100.0
    SUN_POSITION = (50.0, 50.0)
    SUN_RADIUS = 10.0
    MAX_SPEED = 6.0
    MAX_TURNS = 500

    def __init__(self, obs: dict, player: int = 0):
        """
        Initialize analyzer with observation data.

        Args:
            obs: Kaggle environment observation dictionary
            player: Current player ID
        """
        self.obs = obs
        self.player = player
        self.turn = obs.get('turn', 1)
        self.angular_velocities = obs.get('angular_velocity', [])
        self.initial_planets = obs.get('initial_planets', [])
        self.comets = obs.get('comets', [])
        self.comet_planet_ids = obs.get('comet_planet_ids', [])
        self.planets = self._parse_planets(obs.get('planets', []))
        self.fleets = self._parse_fleets(obs.get('fleets', []))

        # Calculate derived state
        self.phase = self._detect_game_phase()
        self.my_planets = [p for p in self.planets if p.owner == self.player]
        self.enemy_planets = [p for p in self.planets if p.owner != self.player and p.owner != -1]
        self.neutral_planets = [p for p in self.planets if p.owner == -1]

        # Stats
        self.my_total_ships = sum(p.ships for p in self.my_planets)
        self.my_fleet_ships = sum(f.ships for f in self.fleets if f.owner == self.player)
        self.total_my_ships = self.my_total_ships + self.my_fleet_ships

    def _parse_planets(self, planets_data: List) -> List[Planet]:
        """Parse planet data from observation."""
        planets = []
        for p in planets_data:
            planet = Planet(
                id=p[0],
                owner=p[1],
                x=p[2],
                y=p[3],
                radius=p[4],
                ships=p[5],
                production=p[6]
            )
            # Add angular velocity if available
            for av in self.angular_velocities:
                if av[0] == planet.id:
                    planet.angular_velocity = av[1]
                    planet.angle = av[2]
                    break
            planets.append(planet)
        return planets

    def _parse_fleets(self, fleets_data: List) -> List[Fleet]:
        """Parse fleet data from observation."""
        return [
            Fleet(
                id=f[0],
                owner=f[1],
                x=f[2],
                y=f[3],
                angle=f[4],
                from_planet_id=f[5],
                ships=f[6]
            )
            for f in fleets_data
        ]

    def _detect_game_phase(self) -> GamePhase:
        """Detect current game phase based on turn count."""
        if self.turn <= 100:
            return GamePhase.EARLY
        elif self.turn <= 300:
            return GamePhase.MID
        else:
            return GamePhase.LATE

    def calculate_fleet_speed(self, ships: int) -> float:
        """
        Calculate fleet speed based on ship count.

        Formula from competition rules:
        speed = 1.0 + (maxSpeed - 1.0) * (log(ships) / log(1000)) ^ 1.5
        """
        if ships <= 0:
            return 1.0
        return 1.0 + (self.MAX_SPEED - 1.0) * (math.log(ships) / math.log(1000)) ** 1.5

    def estimate_fleet_travel_time(self, from_planet: Planet, to_planet: Planet,
                                   ships: int = 100) -> float:
        """
        Estimate turns for a fleet to travel between planets.

        Accounts for average speed based on ship count.
        """
        distance = from_planet.distance_to(to_planet)
        avg_speed = self.calculate_fleet_speed(ships)
        return distance / avg_speed

    def will_fleet_hit_sun(self, start_x: float, start_y: float,
                           angle: float, distance: float) -> bool:
        """
        Check if a fleet trajectory will cross the sun.

        Uses parametric line-circle intersection.
        """
        # Parametric line: (x, y) = (start_x, start_y) + t * (cos(angle), sin(angle))
        # Circle: (x - 50)^2 + (y - 50)^2 = 10^2

        dx = math.cos(angle)
        dy = math.sin(angle)

        # Quadratic coefficients
        a = dx * dx + dy * dy
        b = 2 * (start_x * dx + start_y * dy - 50 * dx - 50 * dy)
        c = (start_x - 50) ** 2 + (start_y - 50) ** 2 - self.SUN_RADIUS ** 2

        discriminant = b * b - 4 * a * c

        if discriminant < 0:
            return False

        # Calculate intersection points
        sqrt_disc = math.sqrt(discriminant)
        t1 = (-b - sqrt_disc) / (2 * a)
        t2 = (-b + sqrt_disc) / (2 * a)

        # Check if intersection occurs within travel distance
        if t1 > 0 and t1 < distance:
            return True
        if t2 > 0 and t2 < distance:
            return True

        return False

    def get_planet_at_position(self, x: float, y: float, tolerance: float = 1.0) -> Optional[Planet]:
        """Find planet at approximate position."""
        for planet in self.planets:
            dist = math.sqrt((planet.x - x) ** 2 + (planet.y - y) ** 2)
            if dist <= planet.radius + tolerance:
                return planet
        return None

    def predict_planet_position(self, planet: Planet, turns_ahead: int) -> Tuple[float, float]:
        """
        Predict planet position after given turns.

        For orbiting planets, accounts for angular velocity.
        """
        if planet.angular_velocity == 0:
            return (planet.x, planet.y)

        # Calculate new angle
        new_angle = planet.angle + planet.angular_velocity * turns_ahead

        # Calculate orbit radius from sun
        orbit_radius = math.sqrt((planet.x - 50) ** 2 + (planet.y - 50) ** 2)

        # New position
        new_x = 50 + orbit_radius * math.cos(new_angle)
        new_y = 50 + orbit_radius * math.sin(new_angle)

        return (new_x, new_y)

    def score_all_targets(self) -> List[Tuple[Planet, float]]:
        """
        Score all possible target planets.

        Returns list of (planet, score) tuples sorted by score descending.
        """
        targets = []
        for planet in self.planets:
            if planet.owner == self.player:
                continue
            score = planet.score_value(self.phase)

            # Apply threat adjustment
            threat_factor = self._calculate_threat_factor(planet)
            score *= threat_factor

            targets.append((planet, score))

        return sorted(targets, key=lambda x: x[1], reverse=True)

    def _calculate_threat_factor(self, planet: Planet) -> float:
        """
        Calculate threat factor for targeting a planet.

        Returns multiplier: <1.0 means risky, >1.0 means safe.
        """
        if planet.owner == -1:
            return 1.0  # Neutrals are safe

        # Check for enemy fleets heading to this planet
        threat_ships = 0
        for fleet in self.fleets:
            if fleet.owner != self.player and fleet.owner != -1:
                # Simplified: just count ships
                threat_ships += fleet.ships

        if threat_ships == 0:
            return 1.2  # Safe to attack

        # Risky target
        return 0.8

    def get_weakest_enemy_planet(self) -> Optional[Planet]:
        """Find the weakest (fewest ships) enemy planet."""
        if not self.enemy_planets:
            return None
        return min(self.enemy_planets, key=lambda p: p.ships)

    def get_strongest_home_planet(self) -> Optional[Planet]:
        """Find the strongest (most ships) friendly planet."""
        if not self.my_planets:
            return None
        return max(self.my_planets, key=lambda p: p.ships)

    def get_best_neutral_target(self) -> Optional[Planet]:
        """
        Find the best neutral planet to capture.

        Considers production, distance, and ship count.
        """
        if not self.neutral_planets:
            return None

        candidates = []
        for planet in self.neutral_planets:
            # Score based on production/distance ratio
            best_source = self.get_nearest_friendly_planet(planet)
            if best_source:
                dist = best_source.distance_to(planet)
                score = planet.production / max(dist, 1)
                candidates.append((planet, score, best_source))

        if not candidates:
            return None

        return max(candidates, key=lambda x: x[1])[0]

    def get_nearest_friendly_planet(self, target: Planet) -> Optional[Planet]:
        """Find nearest friendly planet to a target."""
        if not self.my_planets:
            return None

        nearest = None
        min_dist = float('inf')

        for planet in self.my_planets:
            dist = planet.distance_to(target)
            if dist < min_dist:
                min_dist = dist
                nearest = planet

        return nearest

    def get_expandable_planets(self, min_ships: int = 20) -> List[Planet]:
        """
        Get planets with enough ships for expansion.

        Args:
            min_ships: Minimum ship count to consider for expansion

        Returns:
            List of planets sorted by strategic value
        """
        expandable = [p for p in self.my_planets if p.ships >= min_ships]
        return sorted(expandable, key=lambda p: p.production, reverse=True)

    def count_total_players(self) -> int:
        """Count number of active players (excluding neutral)."""
        owners = set()
        for planet in self.planets:
            if planet.owner != -1:
                owners.add(planet.owner)
        return len(owners)

    def get_player_ship_counts(self) -> Dict[int, int]:
        """Get total ship counts for all players."""
        counts = {}
        for planet in self.planets:
            owner = planet.owner
            if owner == -1:
                continue
            counts[owner] = counts.get(owner, 0) + planet.ships

        for fleet in self.fleets:
            owner = fleet.owner
            if owner == -1:
                continue
            counts[owner] = counts.get(owner, 0) + fleet.ships

        return counts

    def is_losing(self) -> bool:
        """Check if current player is losing."""
        counts = self.get_player_ship_counts()
        if not counts:
            return False
        my_count = counts.get(self.player, 0)
        max_count = max(counts.values())
        return my_count < max_count

    def get_aggression_ratio(self) -> float:
        """
        Calculate ratio of enemy ships vs friendly ships.

        >1.0 means we're being outproduced
        """
        counts = self.get_player_ship_counts()
        my_ships = counts.get(self.player, 0)

        if my_ships == 0:
            return 1.0

        # Sum all other players
        enemy_ships = sum(counts.get(k, 0) for k in counts if k != self.player)

        return enemy_ships / my_ships if my_ships > 0 else 0

    def recommend_strategy(self) -> str:
        """
        Recommend best strategy based on game state.

        Returns strategy name string.
        """
        if self.phase == GamePhase.EARLY:
            if len(self.my_planets) <= 1:
                return 'greedy'
            return 'hybrid'

        elif self.phase == GamePhase.MID:
            if self.is_losing():
                if self.get_aggression_ratio() > 1.5:
                    return 'defensive'
                return 'aggressive'
            return 'hybrid'

        else:  # LATE
            if self.is_losing():
                return 'aggressive'
            return 'hybrid'
