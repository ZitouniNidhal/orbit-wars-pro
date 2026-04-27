import React from 'react';
import { Player, GamePhase } from '../types';
import { PLAYER_COLORS } from '../utils/constants';

interface StatsPanelProps {
  players: Player[];
  currentPlayer: number;
  turn: number;
  phase: GamePhase;
  myPlanets: number;
  enemyPlanets: number;
  neutralPlanets: number;
  myShips: number;
  myFleetShips: number;
  recommendedStrategy: string;
}

const StatsPanel: React.FC<StatsPanelProps> = ({
  players,
  currentPlayer,
  turn,
  phase,
  myPlanets,
  enemyPlanets,
  neutralPlanets,
  myShips,
  myFleetShips,
  recommendedStrategy,
}) => {
  const getPhaseColor = (phase: GamePhase) => {
    switch (phase) {
      case 'EARLY':
        return 'text-green-400';
      case 'MID':
        return 'text-yellow-400';
      case 'LATE':
        return 'text-red-400';
      default:
        return 'text-gray-400';
    }
  };

  return (
    <div className="bg-gray-900 rounded-lg p-4 space-y-4">
      <h2 className="text-lg font-bold text-white border-b border-gray-700 pb-2">
        Game Statistics
      </h2>

      {/* Turn and Phase */}
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-gray-800 rounded p-3">
          <div className="text-gray-400 text-xs uppercase">Turn</div>
          <div className="text-2xl font-bold text-white">{turn}</div>
        </div>
        <div className="bg-gray-800 rounded p-3">
          <div className="text-gray-400 text-xs uppercase">Phase</div>
          <div className={`text-lg font-bold ${getPhaseColor(phase)}`}>{phase}</div>
        </div>
      </div>

      {/* Planet Counts */}
      <div className="space-y-2">
        <h3 className="text-sm font-semibold text-gray-300">Planets</h3>
        <div className="grid grid-cols-3 gap-2">
          <div className="bg-green-900/30 border border-green-700 rounded p-2 text-center">
            <div className="text-xs text-green-400">Mine</div>
            <div className="text-xl font-bold text-green-400">{myPlanets}</div>
          </div>
          <div className="bg-red-900/30 border border-red-700 rounded p-2 text-center">
            <div className="text-xs text-red-400">Enemy</div>
            <div className="text-xl font-bold text-red-400">{enemyPlanets}</div>
          </div>
          <div className="bg-gray-700/50 border border-gray-600 rounded p-2 text-center">
            <div className="text-xs text-gray-400">Neutral</div>
            <div className="text-xl font-bold text-gray-400">{neutralPlanets}</div>
          </div>
        </div>
      </div>

      {/* Ship Counts */}
      <div className="space-y-2">
        <h3 className="text-sm font-semibold text-gray-300">Ships</h3>
        <div className="grid grid-cols-2 gap-2">
          <div className="bg-gray-800 rounded p-2">
            <div className="text-xs text-gray-400">On Planets</div>
            <div className="text-lg font-bold text-green-400">{myShips}</div>
          </div>
          <div className="bg-gray-800 rounded p-2">
            <div className="text-xs text-gray-400">In Fleets</div>
            <div className="text-lg font-bold text-blue-400">{myFleetShips}</div>
          </div>
        </div>
        <div className="bg-gray-800 rounded p-2">
          <div className="text-xs text-gray-400">Total</div>
          <div className="text-2xl font-bold text-white">{myShips + myFleetShips}</div>
        </div>
      </div>

      {/* Recommended Strategy */}
      <div className="bg-purple-900/30 border border-purple-700 rounded p-3">
        <div className="text-xs text-purple-400 uppercase">Recommended Strategy</div>
        <div className="text-lg font-bold text-purple-300 capitalize">{recommendedStrategy}</div>
      </div>

      {/* Player List */}
      <div className="space-y-2">
        <h3 className="text-sm font-semibold text-gray-300">Players</h3>
        <div className="space-y-1">
          {players.map((player) => (
            <div
              key={player.id}
              className={`flex items-center justify-between p-2 rounded ${
                player.id === currentPlayer ? 'bg-gray-800' : 'bg-gray-800/50'
              }`}
            >
              <div className="flex items-center gap-2">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: PLAYER_COLORS[player.id] }}
                />
                <span className="text-sm text-white">
                  {player.name || `Player ${player.id}`}
                </span>
                {player.id === currentPlayer && (
                  <span className="text-xs text-green-400">(You)</span>
                )}
              </div>
              <span className="text-sm font-mono text-gray-400">
                {player.totalShips} ships
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default StatsPanel;
