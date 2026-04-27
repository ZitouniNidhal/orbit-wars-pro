import React, { useState } from 'react';
import { Planet } from '../types';

interface ActionPlannerProps {
  planets: Planet[];
  selectedPlanet: number | null;
  onAddAction: (from: number, to: number, angle: number, ships: number) => void;
  plannedActions: Array<{ from: number; to: number; angle: number; ships: number }>;
  onRemoveAction: (index: number) => void;
  currentPlayer: number;
}

const ActionPlanner: React.FC<ActionPlannerProps> = ({
  planets,
  selectedPlanet,
  onAddAction,
  plannedActions,
  onRemoveAction,
  currentPlayer,
}) => {
  const [targetId, setTargetId] = useState<string>('');
  const [ships, setShips] = useState<string>('20');

  const myPlanets = planets.filter((p) => p.owner === currentPlayer);
  const selectedPlanetData = planets.find((p) => p.id === selectedPlanet);

  const handleAddAction = () => {
    if (!selectedPlanet || !targetId || !ships) return;

    const targetIdNum = parseInt(targetId);
    const shipsNum = parseInt(ships);

    if (isNaN(targetIdNum) || isNaN(shipsNum)) return;

    const targetPlanet = planets.find((p) => p.id === targetIdNum);
    if (!targetPlanet) return;

    const angle = Math.atan2(
      targetPlanet.y - (selectedPlanetData?.y || 0),
      targetPlanet.x - (selectedPlanetData?.x || 0)
    );

    onAddAction(selectedPlanet, targetIdNum, angle, shipsNum);
    setTargetId('');
    setShips('20');
  };

  return (
    <div className="bg-gray-900 rounded-lg p-4">
      <h2 className="text-lg font-bold text-white border-b border-gray-700 pb-2 mb-4">
        Fleet Command
      </h2>

      {/* Selected Planet Info */}
      {selectedPlanetData && (
        <div className="bg-gray-800 rounded p-3 mb-4">
          <div className="text-sm text-gray-400 mb-1">Selected Planet</div>
          <div className="flex items-center justify-between">
            <div>
              <div className="text-white font-semibold">
                Planet {selectedPlanetData.id}
                {selectedPlanetData.owner === currentPlayer && (
                  <span className="ml-2 text-xs text-green-400">(Your planet)</span>
                )}
              </div>
              <div className="text-xs text-gray-400">
                Ships: {selectedPlanetData.ships} | Production: +{selectedPlanetData.production}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Action Form */}
      {selectedPlanetData && selectedPlanetData.owner === currentPlayer && (
        <div className="space-y-3 mb-4">
          <div>
            <label className="text-sm text-gray-400 mb-1 block">Target Planet ID</label>
            <input
              type="number"
              value={targetId}
              onChange={(e) => setTargetId(e.target.value)}
              placeholder="Enter planet ID"
              className="w-full bg-gray-800 text-white rounded px-3 py-2 border border-gray-700 focus:border-purple-500 outline-none"
            />
          </div>
          <div>
            <label className="text-sm text-gray-400 mb-1 block">Number of Ships</label>
            <input
              type="number"
              value={ships}
              onChange={(e) => setShips(e.target.value)}
              placeholder="20"
              min="1"
              max={selectedPlanetData.ships - 5}
              className="w-full bg-gray-800 text-white rounded px-3 py-2 border border-gray-700 focus:border-purple-500 outline-none"
            />
            <div className="text-xs text-gray-500 mt-1">
              Max: {selectedPlanetData.ships - 5} (keep 5 as garrison)
            </div>
          </div>
          <button
            onClick={handleAddAction}
            disabled={!targetId || !ships}
            className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-700 disabled:text-gray-500 text-white font-semibold py-2 rounded transition-colors"
          >
            Launch Fleet
          </button>
        </div>
      )}

      {/* Planned Actions */}
      {plannedActions.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-gray-300 mb-2">Planned Actions</h3>
          <div className="space-y-2">
            {plannedActions.map((action, index) => {
              const fromPlanet = planets.find((p) => p.id === action.from);
              const toPlanet = planets.find((p) => p.id === action.to);
              return (
                <div
                  key={index}
                  className="bg-gray-800 rounded p-2 flex items-center justify-between"
                >
                  <div className="text-sm">
                    <span className="text-green-400">P{action.from}</span>
                    <span className="text-gray-400 mx-2">→</span>
                    <span className="text-red-400">P{action.to}</span>
                    <span className="text-gray-500 ml-2">
                      ({action.ships} ships)
                    </span>
                  </div>
                  <button
                    onClick={() => onRemoveAction(index)}
                    className="text-red-400 hover:text-red-300 text-sm"
                  >
                    ✕
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Quick Select */}
      {selectedPlanet && (
        <div className="mt-4">
          <h3 className="text-sm font-semibold text-gray-300 mb-2">Quick Select Target</h3>
          <div className="grid grid-cols-4 gap-1 max-h-40 overflow-y-auto">
            {planets
              .filter((p) => p.id !== selectedPlanet)
              .map((planet) => (
                <button
                  key={planet.id}
                  onClick={() => setTargetId(planet.id.toString())}
                  className={`p-2 rounded text-xs ${
                    parseInt(targetId) === planet.id
                      ? 'bg-purple-600 text-white'
                      : planet.owner === currentPlayer
                      ? 'bg-green-900/50 text-green-300 hover:bg-green-800'
                      : planet.owner === -1
                      ? 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                      : 'bg-red-900/50 text-red-300 hover:bg-red-800'
                  }`}
                >
                  P{planet.id}
                </button>
              ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ActionPlanner;
