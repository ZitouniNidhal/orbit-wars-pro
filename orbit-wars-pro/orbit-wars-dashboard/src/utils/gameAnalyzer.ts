import { Planet, Fleet, Player, GamePhase } from '../types';

export function parsePlanets(planetsData: number[][]): Planet[] {
  return planetsData.map((p) => ({
    id: p[0],
    owner: p[1],
    x: p[2],
    y: p[3],
    radius: p[4],
    ships: p[5],
    production: p[6],
  }));
}

export function parseFleets(fleetsData: number[][]): Fleet[] {
  return fleetsData.map((f) => ({
    id: f[0],
    owner: f[1],
    x: f[2],
    y: f[3],
    angle: f[4],
    fromPlanetId: f[5],
    ships: f[6],
  }));
}

export function parsePlayers(
  planets: Planet[],
  fleets: Fleet[],
  currentPlayer: number
): Player[] {
  const playerMap: Record<number, { ships: number; planets: number }> = {};

  // Count planets and ships
  planets.forEach((planet) => {
    if (planet.owner === -1) return;
    if (!playerMap[planet.owner]) {
      playerMap[planet.owner] = { ships: 0, planets: 0 };
    }
    playerMap[planet.owner].ships += planet.ships;
    playerMap[planet.owner].planets += 1;
  });

  // Count fleet ships
  fleets.forEach((fleet) => {
    if (fleet.owner === -1) return;
    if (!playerMap[fleet.owner]) {
      playerMap[fleet.owner] = { ships: 0, planets: 0 };
    }
    playerMap[fleet.owner].ships += fleet.ships;
  });

  return Object.entries(playerMap).map(([id, data]) => ({
    id: parseInt(id),
    totalShips: data.ships,
    planets: data.planets,
  }));
}

export function detectGamePhase(turn: number): GamePhase {
  if (turn <= 100) return 'EARLY';
  if (turn <= 300) return 'MID';
  return 'LATE';
}

export function calculateRecommendedStrategy(
  myPlanets: number,
  enemyPlanets: number,
  myShips: number,
  totalEnemyShips: number,
  phase: GamePhase
): string {
  const aggressionRatio = totalEnemyShips / Math.max(myShips, 1);

  if (phase === 'EARLY') {
    return myPlanets <= 1 ? 'greedy' : 'hybrid';
  }

  if (aggressionRatio > 1.5) {
    return 'defensive';
  }

  if (myPlanets < enemyPlanets && aggressionRatio < 0.8) {
    return 'aggressive';
  }

  return 'hybrid';
}

export function calculateFleetSpeed(ships: number): number {
  if (ships <= 0) return 1.0;
  const maxSpeed = 6.0;
  return 1.0 + (maxSpeed - 1.0) * Math.pow(Math.log(ships) / Math.log(1000), 1.5);
}

export function distance(x1: number, y1: number, x2: number, y2: number): number {
  return Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
}

export function angleTo(x1: number, y1: number, x2: number, y2: number): number {
  return Math.atan2(y2 - y1, x2 - x1);
}

export function estimateTravelTime(
  from: Planet,
  to: Planet,
  ships: number = 100
): number {
  const dist = distance(from.x, from.y, to.x, to.y);
  const speed = calculateFleetSpeed(ships);
  return dist / speed;
}
