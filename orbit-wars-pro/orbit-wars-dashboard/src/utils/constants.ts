export const BOARD_SIZE = 100;
export const SUN_RADIUS = 10;
export const SUN_POSITION: [number, number] = [50, 50];
export const MAX_TURNS = 500;

export const PLAYER_COLORS: Record<number, string> = {
  0: '#22c55e', // Green
  1: '#ef4444', // Red
  2: '#3b82f6', // Blue
  3: '#f59e0b', // Orange
  4: '#8b5cf6', // Purple
  5: '#ec4899', // Pink
};

export const DEFAULT_OBSERVATION = {
  turn: 1,
  player: 0,
  planets: [
    [0, 0, 25, 25, 2.5, 20, 3],
    [1, -1, 40, 35, 2.0, 15, 2],
    [2, -1, 55, 45, 2.5, 30, 4],
    [3, 1, 70, 60, 2.5, 25, 3],
    [4, 2, 30, 70, 2.0, 18, 2],
    [5, -1, 75, 25, 1.8, 12, 1],
    [6, 0, 45, 75, 2.2, 22, 3],
    [7, 3, 65, 35, 2.0, 20, 2],
  ],
  fleets: [
    [0, 0, 35, 32, 0.5, 0, 8],
    [1, 1, 60, 55, 3.5, 3, 10],
  ],
  angular_velocity: [
    [0, 0.0, 0.0],
    [6, 0.03, 0.0],
  ],
  initial_planets: [],
  comets: [],
  comet_planet_ids: [],
};
