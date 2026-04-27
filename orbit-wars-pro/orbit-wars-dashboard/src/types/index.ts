export interface Planet {
  id: number;
  owner: number;
  x: number;
  y: number;
  radius: number;
  ships: number;
  production: number;
  angularVelocity?: number;
  angle?: number;
}

export interface Fleet {
  id: number;
  owner: number;
  x: number;
  y: number;
  angle: number;
  fromPlanetId: number;
  ships: number;
}

export interface Player {
  id: number;
  name?: string;
  totalShips: number;
  planets: number;
}

export type GamePhase = 'EARLY' | 'MID' | 'LATE';

export interface GameState {
  turn: number;
  player: number;
  planets: Planet[];
  fleets: Fleet[];
  players: Player[];
  phase: GamePhase;
  recommendedStrategy: string;
}

export interface PlannedAction {
  from: number;
  to: number;
  angle: number;
  ships: number;
}
