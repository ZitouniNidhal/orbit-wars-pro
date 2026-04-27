

import math
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from enum import Enum

# ========================================
# CONFIGURATION CONSTANTS
# ========================================

BOARD_SIZE = 100.0
SUN_POSITION = (50.0, 50.0)
SUN_RADIUS = 10.0
MAX_SPEED = 6.0
MAX_TURNS = 500

# ========================================
# DATA STRUCTURES
# ========================================

class GamePhase(Enum):
    """Game phases based on turn count."""
    EARLY = 1   # Turns 1-100
    MID = 2     # Turns 101-300
    LATE = 3    # Turns 301-500

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

# ========================================
# GAME ANALYZER
# ========================================

class GameAnalyzer:
    """
    Comprehensive game state analyzer.

    Provides utilities for understanding the current game state
    and calculating strategic values for decision making.
    """

    def __init__(self, obs: dict, player: int = 0):
        """Initialize analyzer with observation data."""
        self.obs = obs
        self.player = player
        self.turn = obs.get('turn', 1)
        self.angular_velocities = obs.get('angular_velocity', [])

        # Parse planets and fleets
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

    def will_fleet_hit_sun(self, start_x: float, start_y: float,
                           angle: float, distance: float) -> bool:
        """Check if a fleet trajectory will cross the sun."""
        dx = math.cos(angle)
        dy = math.sin(angle)

        # Quadratic coefficients for line-circle intersection
        a = dx * dx + dy * dy
        b = 2 * (start_x * dx + start_y * dy - 50 * dx - 50 * dy)
        c = (start_x - 50) ** 2 + (start_y - 50) ** 2 - SUN_RADIUS ** 2

        discriminant = b * b - 4 * a * c
        if discriminant < 0:
            return False

        sqrt_disc = math.sqrt(discriminant)
        t1 = (-b - sqrt_disc) / (2 * a)
        t2 = (-b + sqrt_disc) / (2 * a)

        # Check if intersection occurs within travel distance
        if t1 > 0 and t1 < distance:
            return True
        if t2 > 0 and t2 < distance:
            return True

        return False

    def find_safe_launch_angle(self, source: Planet, target: Planet,
                                max_attempts: int = 36) -> Tuple[float, bool]:
        """Find a safe angle to launch fleet that avoids the sun."""
        direct_angle = source.angle_to(target)
        direct_distance = source.distance_to(target)

        # Check direct path
        if not self.will_fleet_hit_sun(source.x, source.y, direct_angle, direct_distance):
            return (direct_angle, True)

        # Try angles offset from direct path
        angle_step = 2 * math.pi / max_attempts
        max_offset = math.pi / 2

        for i in range(1, max_attempts + 1):
            offset = i * angle_step
            for sign in [1, -1]:
                angle = direct_angle + sign * min(offset, max_offset)
                if not self.will_fleet_hit_sun(source.x, source.y, angle, direct_distance):
                    return (angle, True)

        return (direct_angle, False)

    def get_expandable_planets(self, min_ships: int = 15) -> List[Planet]:
        """Get planets with enough ships for expansion."""
        expandable = [p for p in self.my_planets if p.ships >= min_ships]
        return sorted(expandable, key=lambda p: p.production, reverse=True)

    def is_losing(self) -> bool:
        """Check if current player is losing."""
        counts = self.get_player_ship_counts()
        if not counts:
            return False
        my_count = counts.get(self.player, 0)
        max_count = max(counts.values())
        return my_count < max_count

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

    def get_aggression_ratio(self) -> float:
        """Calculate ratio of enemy ships vs friendly ships."""
        counts = self.get_player_ship_counts()
        my_ships = counts.get(self.player, 0)
        if my_ships == 0:
            return 1.0
        enemy_ships = sum(counts.get(k, 0) for k in counts if k != self.player)
        return enemy_ships / my_ships if my_ships > 0 else 0

    def recommend_strategy(self) -> str:
        """Recommend best strategy based on game state."""
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

# ========================================
# STRATEGY IMPLEMENTATIONS
# ========================================

class GreedyStrategy:
    """Greedy expansion strategy focusing on capturing neutrals."""

    def __init__(self, min_ships_for_attack: int = 15):
        self.min_ships_for_attack = min_ships_for_attack

    def get_actions(self, analyzer: GameAnalyzer) -> List[List]:
        """Generate actions for greedy strategy."""
        actions = []
        commanded_planets = set()
        expandable = analyzer.get_expandable_planets(self.min_ships_for_attack)

        for source in expandable:
            if source.id in commanded_planets:
                continue

            best_target = None
            best_score = -1

            for neutral in analyzer.neutral_planets:
                dist = source.distance_to(neutral)
                if dist < 1:
                    continue

                angle = source.angle_to(neutral)
                if analyzer.will_fleet_hit_sun(source.x, source.y, angle, dist):
                    continue

                score = neutral.production * 10 / dist
                if score > best_score:
                    best_score = score
                    best_target = neutral

            if best_target and best_score > 0:
                ships_available = source.ships - 10
                ships_needed = best_target.ships + 1
                ships_to_send = max(ships_needed, min(ships_available, 50))

                if ships_to_send >= self.min_ships_for_attack:
                    safe_angle = analyzer.find_safe_launch_angle(source, best_target)[0]
                    actions.append([source.id, safe_angle, ships_to_send])
                    commanded_planets.add(source.id)

        return actions


class AggressiveStrategy:
    """Aggressive attack strategy focusing on enemy elimination."""

    def __init__(self, min_ships_for_attack: int = 20, attack_ratio: float = 0.7):
        self.min_ships_for_attack = min_ships_for_attack
        self.attack_ratio = attack_ratio

    def get_actions(self, analyzer: GameAnalyzer) -> List[List]:
        """Generate actions for aggressive strategy."""
        actions = []
        commanded = set()
        expandable = analyzer.get_expandable_planets(self.min_ships_for_attack)

        # Priority 1: Attack weakest enemy planets
        for source in expandable:
            if source.id in commanded:
                continue

            weakest_enemy = min(analyzer.enemy_planets, key=lambda p: p.ships) if analyzer.enemy_planets else None
            if not weakest_enemy:
                continue

            ships_available = source.ships - 10
            ships_needed = weakest_enemy.ships + 1

            if ships_available >= ships_needed * 1.2:
                ships_to_send = int(ships_available * self.attack_ratio)
                safe_angle = analyzer.find_safe_launch_angle(source, weakest_enemy)[0]
                actions.append([source.id, safe_angle, ships_to_send])
                commanded.add(source.id)

        # Priority 2: Attack any reachable enemy
        if len(actions) < 2:
            for source in expandable:
                if source.id in commanded:
                    continue

                for enemy in analyzer.enemy_planets:
                    dist = source.distance_to(enemy)
                    if dist > 60:
                        continue

                    angle = source.angle_to(enemy)
                    if analyzer.will_fleet_hit_sun(source.x, source.y, angle, dist):
                        continue

                    ships_available = source.ships - 8
                    if ships_available >= (enemy.ships + 1) * 1.1:
                        ships_to_send = max(enemy.ships + 1, int(ships_available * self.attack_ratio))
                        safe_angle = analyzer.find_safe_launch_angle(source, enemy)[0]
                        actions.append([source.id, safe_angle, ships_to_send])
                        commanded.add(source.id)
                        break

        return actions


class DefensiveStrategy:
    """Defensive consolidation strategy."""

    def __init__(self, garrison_target: int = 15, reinforce_threshold: int = 25):
        self.garrison_target = garrison_target
        self.reinforce_threshold = reinforce_threshold

    def get_actions(self, analyzer: GameAnalyzer) -> List[List]:
        """Generate actions for defensive strategy."""
        actions = []
        vulnerable = []
        well_defended = []

        for planet in analyzer.my_planets:
            if planet.ships < self.garrison_target:
                vulnerable.append(planet)
            else:
                well_defended.append(planet)

        # Priority 1: Reinforce vulnerable planets
        for vulnerable_planet in vulnerable:
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
                    angle = best_reinforcer.angle_to(vulnerable_planet)
                    actions.append([best_reinforcer.id, angle, ships_to_send])
                    well_defended = [p for p in well_defended if p.id != best_reinforcer.id]

        # Priority 2: Capture nearby neutrals if well defended
        if len(actions) < 2:
            for planet in well_defended:
                if planet.ships < self.reinforce_threshold:
                    continue

                best_target = None
                best_score = -1

                for neutral in analyzer.neutral_planets:
                    dist = planet.distance_to(neutral)
                    if dist > 40:
                        continue

                    angle = planet.angle_to(neutral)
                    if analyzer.will_fleet_hit_sun(planet.x, planet.y, angle, dist):
                        continue

                    score = neutral.production * 10 / max(dist, 1)
                    if score > best_score:
                        best_score = score
                        best_target = neutral

                if best_target:
                    ships_available = planet.ships - self.garrison_target
                    ships_to_send = max(best_target.ships + 1, min(20, ships_available))
                    if ships_to_send >= 10:
                        safe_angle = analyzer.find_safe_launch_angle(planet, best_target)[0]
                        actions.append([planet.id, safe_angle, ships_to_send])
                        break

        return actions


class HybridStrategy:
    """Hybrid strategy combining greedy, aggressive, and defensive approaches."""

    def __init__(self):
        self.greedy = GreedyStrategy(min_ships_for_attack=15)
        self.aggressive = AggressiveStrategy(min_ships_for_attack=20, attack_ratio=0.6)
        self.defensive = DefensiveStrategy(garrison_target=12, reinforce_threshold=22)

    def get_actions(self, analyzer: GameAnalyzer) -> List[List]:
        """Generate actions using hybrid approach."""
        actions = []
        action_sources = set()

        phase = analyzer.phase
        is_losing = analyzer.is_losing()
        aggression_ratio = analyzer.get_aggression_ratio()

        if phase == GamePhase.EARLY:
            primary_mode = 'greedy'
        elif phase == GamePhase.MID:
            if is_losing and aggression_ratio > 1.3:
                primary_mode = 'defensive'
            elif len(analyzer.my_planets) < 2:
                primary_mode = 'greedy'
            else:
                primary_mode = 'balanced'
        else:
            if is_losing:
                primary_mode = 'aggressive'
            else:
                primary_mode = 'balanced'

        if primary_mode == 'greedy':
            actions = self.greedy.get_actions(analyzer)
            actions.extend(self.defensive.get_actions(analyzer)[:1])

        elif primary_mode == 'aggressive':
            aggressive_actions = self.aggressive.get_actions(analyzer)
            actions.extend(aggressive_actions[:2])

            if len(actions) < 2:
                greedy_actions = self.greedy.get_actions(analyzer)
                for action in greedy_actions:
                    if len(actions) >= 3:
                        break
                    if action[0] not in action_sources:
                        actions.append(action)
                        action_sources.add(action[0])

        elif primary_mode == 'defensive':
            defensive_actions = self.defensive.get_actions(analyzer)
            actions.extend(defensive_actions[:2])

            easy_kills = self._find_easy_kills(analyzer)
            for kill in easy_kills:
                if len(actions) >= 3:
                    break
                if kill[0] not in action_sources:
                    actions.append(kill)
                    action_sources.add(kill[0])

        else:
            greedy_actions = self.greedy.get_actions(analyzer)
            for action in greedy_actions[:1]:
                actions.append(action)
                action_sources.add(action[0])

            easy_kills = self._find_easy_kills(analyzer)
            for kill in easy_kills:
                if len(actions) >= 2:
                    break
                if kill[0] not in action_sources:
                    actions.append(kill)
                    action_sources.add(kill[0])

            if len(actions) < 2:
                defensive_actions = self.defensive.get_actions(analyzer)
                for action in defensive_actions[:1]:
                    if action[0] not in action_sources:
                        actions.append(action)
                        action_sources.add(action[0])

        return actions[:3]

    def _find_easy_kills(self, analyzer: GameAnalyzer) -> List[List]:
        """Find weak enemy planets that can be easily captured."""
        easy_kills = []

        for source in analyzer.get_expandable_planets(15):
            for enemy in analyzer.enemy_planets:
                dist = source.distance_to(enemy)
                if dist > 50:
                    continue

                angle = source.angle_to(enemy)
                if analyzer.will_fleet_hit_sun(source.x, source.y, angle, dist):
                    continue

                ships_available = source.ships - 10
                ships_needed = enemy.ships + 1

                if ships_available >= ships_needed * 1.2:
                    ships_to_send = max(ships_needed, int(ships_available * 0.6))
                    safe_angle = analyzer.find_safe_launch_angle(source, enemy)[0]
                    easy_kills.append([source.id, safe_angle, ships_to_send])
                    break

        return easy_kills

# ========================================
# MAIN AGENT - ORBIT WARS PRO
# ========================================

class OrbitWarsPro:
    """Professional Orbit Wars agent with multi-strategy support."""

    STRATEGY_ADAPTIVE = 'adaptive'

    def __init__(self, strategy_mode: str = 'adaptive', debug: bool = False):
        """Initialize Orbit Wars Pro agent."""
        self.strategy_mode = strategy_mode
        self.debug = debug

        self.strategies = {
            'greedy': GreedyStrategy(min_ships_for_attack=15),
            'aggressive': AggressiveStrategy(min_ships_for_attack=18, attack_ratio=0.65),
            'defensive': DefensiveStrategy(garrison_target=12, reinforce_threshold=22),
            'hybrid': HybridStrategy(),
        }

        self.current_strategy = strategy_mode

    def act(self, obs: dict) -> List[List]:
        """Generate actions based on observation."""
        analyzer = GameAnalyzer(obs, obs.get('player', 0))

        if self.strategy_mode == self.STRATEGY_ADAPTIVE:
            self.current_strategy = analyzer.recommend_strategy()
        else:
            self.current_strategy = self.strategy_mode

        strategy = self.strategies.get(self.current_strategy, self.strategies['hybrid'])
        return strategy.get_actions(analyzer)

# ========================================
# KAGGLE ENTRY POINT
# ========================================

# Global instance
_agent_instance = None

def orbit_wars_agent(obs: dict) -> List[List]:
    """
    Main agent function for Kaggle submission.

    This is the entry point for the Kaggle environment.
    The last def in the file must accept 'observation' and return 'action'.

    Args:
        obs: Kaggle environment observation

    Returns:
        List of fleet commands [[from_id, angle, ships], ...]
    """
    global _agent_instance

    if _agent_instance is None:
        _agent_instance = OrbitWarsPro(strategy_mode='adaptive', debug=False)

    return _agent_instance.act(obs)

# Kaggle simulation interface - the LAST def in the file
def main(observation):
    """
    Kaggle simulation entry point.

    This function is called by the Kaggle simulation environment.

    Args:
        observation: Game observation from the simulation

    Returns:
        List of fleet commands
    """
    return orbit_wars_agent(observation)