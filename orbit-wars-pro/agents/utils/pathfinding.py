"""
Pathfinding and Trajectory Utilities

Handles fleet trajectory calculations and path planning.
"""

import math
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from agents.utils.game_analyzer import Planet, Fleet


@dataclass
class Trajectory:
    """Fleet trajectory information."""
    start_x: float
    start_y: float
    end_x: float
    end_y: float
    angle: float
    distance: float
    estimated_turns: float
    hits_sun: bool
    will_collide: bool
    collision_planet: Optional[Planet] = None


class PathFinder:
    """
    Fleet pathfinding and trajectory calculator.

    Calculates optimal trajectories for fleet movement
    and handles collision detection with the sun and planets.
    """

    BOARD_SIZE = 100.0
    SUN_POSITION = (50.0, 50.0)
    SUN_RADIUS = 10.0
    PLANET_COLLISION_BUFFER = 0.5

    def __init__(self, planets: List[Planet]):
        """
        Initialize pathfinder with game state.

        Args:
            planets: List of all planets in the game
        """
        self.planets = planets

    def calculate_angle(self, from_x: float, from_y: float,
                       to_x: float, to_y: float) -> float:
        """
        Calculate angle from one point to another.

        Args:
            from_x, from_y: Starting position
            to_x, to_y: Target position

        Returns:
            Angle in radians
        """
        return math.atan2(to_y - from_y, to_x - from_x)

    def calculate_distance(self, x1: float, y1: float,
                           x2: float, y2: float) -> float:
        """Calculate Euclidean distance between two points."""
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def calculate_trajectory(self, source: Planet, target: Planet,
                             ship_count: int = 100) -> Trajectory:
        """
        Calculate full trajectory for a fleet.

        Args:
            source: Source planet
            target: Target planet
            ship_count: Number of ships (affects speed)

        Returns:
            Trajectory with all movement details
        """
        angle = self.calculate_angle(source.x, source.y, target.x, target.y)
        distance = self.calculate_distance(source.x, source.y, target.x, target.y)

        # Estimate travel time based on ship count
        speed = self._calculate_speed(ship_count)
        estimated_turns = distance / speed

        # Check for sun collision
        hits_sun = self._check_sun_collision(source.x, source.y, angle, distance)

        # Check for planet collision (intermediate)
        collision_planet, will_collide = self._check_intermediate_collision(
            source.x, source.y, angle, distance, target
        )

        return Trajectory(
            start_x=source.x,
            start_y=source.y,
            end_x=target.x,
            end_y=target.y,
            angle=angle,
            distance=distance,
            estimated_turns=estimated_turns,
            hits_sun=hits_sun,
            will_collide=will_collide,
            collision_planet=collision_planet
        )

    def _calculate_speed(self, ships: int) -> float:
        """
        Calculate fleet speed based on ship count.

        Formula: speed = 1.0 + (maxSpeed - 1.0) * (log(ships) / log(1000)) ^ 1.5
        """
        if ships <= 0:
            return 1.0
        max_speed = 6.0
        return 1.0 + (max_speed - 1.0) * (math.log(ships) / math.log(1000)) ** 1.5

    def _check_sun_collision(self, start_x: float, start_y: float,
                              angle: float, distance: float) -> bool:
        """
        Check if trajectory crosses the sun.

        Uses line-circle intersection test.
        """
        dx = math.cos(angle)
        dy = math.sin(angle)

        # Parametric line: (x, y) = start + t * direction
        # Circle: (x - 50)^2 + (y - 50)^2 = r^2

        # Quadratic: at^2 + bt + c = 0
        a = dx * dx + dy * dy
        b = 2 * (start_x * dx + start_y * dy - 50 * dx - 50 * dy)
        c = (start_x - 50) ** 2 + (start_y - 50) ** 2 - self.SUN_RADIUS ** 2

        discriminant = b * b - 4 * a * c

        if discriminant < 0:
            return False

        sqrt_disc = math.sqrt(discriminant)
        t1 = (-b - sqrt_disc) / (2 * a)
        t2 = (-b + sqrt_disc) / (2 * a)

        # Check if intersection is within travel distance
        for t in [t1, t2]:
            if 0 < t < distance / math.sqrt(dx * dx + dy * dy):
                return True

        return False

    def _check_intermediate_collision(self, start_x: float, start_y: float,
                                      angle: float, distance: float,
                                      target: Planet) -> Tuple[Optional[Planet], bool]:
        """
        Check if trajectory collides with intermediate planets.

        Args:
            start_x, start_y: Starting position
            angle: Direction of travel
            distance: Total distance
            target: Intended target planet

        Returns:
            Tuple of (collision planet, will_collide)
        """
        dx = math.cos(angle)
        dy = math.sin(angle)

        # Check each planet except target
        for planet in self.planets:
            if planet.id == target.id:
                continue

            # Line-circle intersection
            fx = start_x - planet.x
            fy = start_y - planet.y

            a = dx * dx + dy * dy
            b = 2 * (fx * dx + fy * dy)
            c = fx * fx + fy * fy - (planet.radius + self.PLANET_COLLISION_BUFFER) ** 2

            discriminant = b * b - 4 * a * c

            if discriminant < 0:
                continue

            sqrt_disc = math.sqrt(discriminant)
            t1 = (-b - sqrt_disc) / (2 * a)
            t2 = (-b + sqrt_disc) / (2 * a)

            # Check if collision occurs before reaching target
            max_t = distance / math.sqrt(dx * dx + dy * dy)
            for t in [t1, t2]:
                if 0 < t < max_t:
                    return (planet, True)

        return (None, False)

    def find_safe_launch_angle(self, source: Planet, target: Planet,
                                max_attempts: int = 36) -> Tuple[float, bool]:
        """
        Find a safe angle to launch fleet that avoids the sun.

        If direct path hits sun, finds alternative angles.

        Args:
            source: Source planet
            target: Target planet
            max_attempts: Number of angle variations to try

        Returns:
            Tuple of (angle, found_safe)
        """
        direct_angle = self.calculate_angle(source.x, source.y, target.x, target.y)
        direct_distance = self.calculate_distance(source.x, source.y, target.x, target.y)

        # Check direct path
        if not self._check_sun_collision(source.x, source.y, direct_angle, direct_distance):
            return (direct_angle, True)

        # Try angles offset from direct path
        angle_step = 2 * math.pi / max_attempts
        max_offset = math.pi / 2  # Don't go more than 90 degrees off

        for i in range(1, max_attempts + 1):
            offset = i * angle_step
            for sign in [1, -1]:
                angle = direct_angle + sign * min(offset, max_offset)
                if not self._check_sun_collision(source.x, source.y, angle, direct_distance):
                    return (angle, True)

        # No safe angle found
        return (direct_angle, False)

    def predict_position(self, fleet: Fleet, turns: int) -> Tuple[float, float]:
        """
        Predict fleet position after given turns.

        Args:
            fleet: Fleet to predict
            turns: Number of turns ahead

        Returns:
            Predicted (x, y) position
        """
        speed = self._calculate_speed(fleet.ships)
        distance = speed * turns

        x = fleet.x + math.cos(fleet.angle) * distance
        y = fleet.y + math.sin(fleet.angle) * distance

        return (x, y)

    def find_fleet_target_planet(self, fleet: Fleet) -> Optional[Planet]:
        """
        Determine which planet a fleet is heading toward.

        Uses the fleet's from_planet_id to identify trajectory.

        Args:
            fleet: Fleet to analyze

        Returns:
            Target planet if determinable
        """
        for planet in self.planets:
            if planet.id == fleet.from_planet_id:
                continue

            # Calculate angle to planet
            angle_to_planet = self.calculate_angle(fleet.x, fleet.y, planet.x, planet.y)
            angle_diff = abs(self._normalize_angle(fleet.angle - angle_to_planet))

            # If angle is close, fleet might be heading here
            if angle_diff < 0.1:  # ~6 degrees tolerance
                dist = self.calculate_distance(fleet.x, fleet.y, planet.x, planet.y)
                if dist < 50:  # Reasonable targeting distance
                    return planet

        return None

    def _normalize_angle(self, angle: float) -> float:
        """Normalize angle to [-pi, pi] range."""
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle

    def get_expansion_options(self, source: Planet,
                              max_distance: float = 50.0) -> List[Tuple[Planet, float]]:
        """
        Get all viable expansion targets from a source planet.

        Args:
            source: Source planet
            max_distance: Maximum travel distance to consider

        Returns:
            List of (target, safety_score) tuples
        """
        options = []

        for planet in self.planets:
            if planet.owner == source.owner:
                continue

            dist = source.distance_to(planet)

            if dist > max_distance:
                continue

            # Check sun collision
            angle = self.calculate_angle(source.x, source.y, planet.x, planet.y)
            hits_sun = self._check_sun_collision(source.x, source.y, angle, dist)

            if hits_sun:
                continue

            # Calculate safety score
            safety = 1.0 - (dist / max_distance)

            options.append((planet, safety))

        return sorted(options, key=lambda x: x[1], reverse=True)
