import { useState, useCallback } from 'react';
import GameCanvas from './components/GameCanvas';
import StatsPanel from './components/StatsPanel';
import StrategySelector, { StrategyMode } from './components/StrategySelector';
import ActionPlanner from './components/ActionPlanner';
import { Planet, Fleet, Player, PlannedAction } from './types';
import {
  parsePlanets,
  parseFleets,
  parsePlayers,
  detectGamePhase,
  calculateRecommendedStrategy,
} from './utils/gameAnalyzer';
import { DEFAULT_OBSERVATION } from './utils/constants';

function App() {
  // Game state
  const [obs, setObs] = useState(DEFAULT_OBSERVATION);
  const [currentPlayer, setCurrentPlayer] = useState(0);
  const [selectedPlanet, setSelectedPlanet] = useState<number | null>(null);
  const [plannedActions, setPlannedActions] = useState<PlannedAction[]>([]);
  const [strategyMode, setStrategyMode] = useState<StrategyMode>('adaptive');
  const [jsonInput, setJsonInput] = useState(JSON.stringify(DEFAULT_OBSERVATION, null, 2));
  const [showJsonEditor, setShowJsonEditor] = useState(false);

  // Parse game data
  const planets = parsePlanets(obs.planets);
  const fleets = parseFleets(obs.fleets);
  const players = parsePlayers(planets, fleets, currentPlayer);
  const phase = detectGamePhase(obs.turn);

  // Calculate stats
  const myPlanets = planets.filter((p) => p.owner === currentPlayer);
  const enemyPlanets = planets.filter((p) => p.owner !== currentPlayer && p.owner !== -1);
  const neutralPlanets = planets.filter((p) => p.owner === -1);
  const myShips = myPlanets.reduce((sum, p) => sum + p.ships, 0);
  const myFleetShips = fleets.filter((f) => f.owner === currentPlayer).reduce((sum, f) => sum + f.ships, 0);

  const totalEnemyShips = players
    .filter((p) => p.id !== currentPlayer)
    .reduce((sum, p) => sum + p.totalShips, 0);

  const recommendedStrategy = calculateRecommendedStrategy(
    myPlanets.length,
    enemyPlanets.length,
    myShips,
    totalEnemyShips,
    phase
  );

  // Handlers
  const handleJsonApply = useCallback(() => {
    try {
      const parsed = JSON.parse(jsonInput);
      setObs(parsed);
      setPlannedActions([]);
      setSelectedPlanet(null);
    } catch (e) {
      alert('Invalid JSON format');
    }
  }, [jsonInput]);

  const handleAddAction = useCallback((from: number, to: number, angle: number, ships: number) => {
    setPlannedActions((prev) => [...prev, { from, to, angle, ships }]);
  }, []);

  const handleRemoveAction = useCallback((index: number) => {
    setPlannedActions((prev) => prev.filter((_, i) => i !== index));
  }, []);

  const handleLoadExample = useCallback(() => {
    const examples = [
      {
        name: 'Early Game',
        data: {
          turn: 15,
          player: 0,
          planets: [
            [0, 0, 25, 25, 2.5, 35, 3],
            [1, -1, 40, 35, 2.0, 20, 2],
            [2, -1, 55, 45, 2.5, 25, 4],
            [3, 1, 70, 60, 2.5, 30, 3],
            [4, 2, 30, 70, 2.0, 25, 2],
            [5, -1, 75, 25, 1.8, 15, 1],
            [6, 0, 45, 75, 2.2, 28, 3],
            [7, 3, 65, 35, 2.0, 22, 2],
          ],
          fleets: [],
          angular_velocity: [],
          initial_planets: [],
          comets: [],
          comet_planet_ids: [],
        },
      },
      {
        name: 'Mid Game',
        data: {
          turn: 180,
          player: 0,
          planets: [
            [0, 0, 25, 25, 2.5, 45, 3],
            [1, 0, 40, 35, 2.0, 32, 2],
            [2, -1, 55, 45, 2.5, 18, 4],
            [3, 1, 70, 60, 2.5, 38, 3],
            [4, 0, 30, 70, 2.0, 25, 2],
            [5, 1, 75, 25, 1.8, 20, 1],
            [6, 2, 45, 75, 2.2, 30, 3],
            [7, 3, 65, 35, 2.0, 28, 2],
            [8, 2, 80, 70, 2.0, 22, 2],
          ],
          fleets: [
            [0, 0, 35, 32, 0.5, 0, 15],
            [1, 1, 60, 50, 3.5, 3, 18],
            [2, 2, 50, 65, 2.1, 6, 12],
          ],
          angular_velocity: [],
          initial_planets: [],
          comets: [],
          comet_planet_ids: [],
        },
      },
      {
        name: 'Late Game',
        data: {
          turn: 350,
          player: 0,
          planets: [
            [0, 0, 25, 25, 2.5, 55, 3],
            [1, 0, 40, 35, 2.0, 42, 2],
            [2, 0, 55, 45, 2.5, 35, 4],
            [3, 1, 70, 60, 2.5, 48, 3],
            [4, 1, 30, 70, 2.0, 30, 2],
            [5, 0, 75, 25, 1.8, 25, 1],
            [6, 2, 45, 75, 2.2, 38, 3],
            [7, 3, 65, 35, 2.0, 32, 2],
            [8, 2, 80, 70, 2.0, 28, 2],
            [9, 1, 85, 50, 2.0, 22, 2],
          ],
          fleets: [
            [0, 0, 35, 32, 0.5, 0, 20],
            [1, 0, 60, 55, 3.8, 2, 25],
            [2, 1, 50, 45, 2.5, 3, 18],
            [3, 2, 60, 68, 2.1, 6, 15],
          ],
          angular_velocity: [],
          initial_planets: [],
          comets: [],
          comet_planet_ids: [],
        },
      },
    ];

    const randomExample = examples[Math.floor(Math.random() * examples.length)];
    setObs(randomExample.data);
    setJsonInput(JSON.stringify(randomExample.data, null, 2));
    setPlannedActions([]);
    setSelectedPlanet(null);
  }, []);

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Header */}
      <header className="bg-gray-900 border-b border-gray-800 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-blue-500 bg-clip-text text-transparent">
              Orbit Wars Pro
            </h1>
            <p className="text-sm text-gray-400">Interactive Game Visualizer & AI Agent</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={handleLoadExample}
              className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm transition-colors"
            >
              Load Example
            </button>
            <button
              onClick={() => setShowJsonEditor(!showJsonEditor)}
              className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm transition-colors"
            >
              {showJsonEditor ? 'Hide Editor' : 'Show Editor'}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="p-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Left Column - Canvas */}
          <div className="lg:col-span-3 space-y-6">
            {/* Game Canvas */}
            <div className="bg-gray-900 rounded-lg p-4">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">Game Board</h2>
                <div className="flex items-center gap-4 text-sm">
                  <span className="text-gray-400">Current Player:</span>
                  <select
                    value={currentPlayer}
                    onChange={(e) => setCurrentPlayer(parseInt(e.target.value))}
                    className="bg-gray-800 text-white px-3 py-1 rounded border border-gray-700"
                  >
                    {players.map((p) => (
                      <option key={p.id} value={p.id}>
                        Player {p.id}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="flex justify-center overflow-auto">
                <GameCanvas
                  planets={planets}
                  fleets={fleets}
                  players={players}
                  currentPlayer={currentPlayer}
                  selectedPlanet={selectedPlanet}
                  onPlanetSelect={setSelectedPlanet}
                  plannedActions={plannedActions}
                />
              </div>
            </div>

            {/* JSON Editor */}
            {showJsonEditor && (
              <div className="bg-gray-900 rounded-lg p-4">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold">Game State JSON</h2>
                  <button
                    onClick={handleJsonApply}
                    className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg text-sm transition-colors"
                  >
                    Apply
                  </button>
                </div>
                <textarea
                  value={jsonInput}
                  onChange={(e) => setJsonInput(e.target.value)}
                  className="w-full h-64 bg-gray-950 text-gray-300 font-mono text-sm p-4 rounded border border-gray-800 focus:border-purple-500 outline-none resize-none"
                  spellCheck={false}
                />
                <p className="text-xs text-gray-500 mt-2">
                  Paste a Kaggle observation JSON here to visualize a game state.
                </p>
              </div>
            )}

            {/* Action Output */}
            {plannedActions.length > 0 && (
              <div className="bg-gray-900 rounded-lg p-4">
                <h2 className="text-lg font-semibold mb-4">Agent Actions (for Kaggle)</h2>
                <pre className="bg-gray-950 text-green-400 font-mono text-sm p-4 rounded overflow-x-auto">
                  {JSON.stringify(
                    plannedActions.map((a) => [a.from, a.angle, a.ships]),
                    null,
                    2
                  )}
                </pre>
              </div>
            )}
          </div>

          {/* Right Column - Panels */}
          <div className="space-y-6">
            <StatsPanel
              players={players}
              currentPlayer={currentPlayer}
              turn={obs.turn}
              phase={phase}
              myPlanets={myPlanets.length}
              enemyPlanets={enemyPlanets.length}
              neutralPlanets={neutralPlanets.length}
              myShips={myShips}
              myFleetShips={myFleetShips}
              recommendedStrategy={recommendedStrategy}
            />

            <StrategySelector
              selectedStrategy={strategyMode}
              onStrategyChange={setStrategyMode}
            />

            <ActionPlanner
              planets={planets}
              selectedPlanet={selectedPlanet}
              onAddAction={handleAddAction}
              plannedActions={plannedActions}
              onRemoveAction={handleRemoveAction}
              currentPlayer={currentPlayer}
            />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 border-t border-gray-800 px-6 py-4 mt-6">
        <div className="flex items-center justify-between text-sm text-gray-500">
          <span>Orbit Wars Pro - Professional AI Agent for Kaggle Competition</span>
          <span>Prize Pool: $50,000</span>
        </div>
      </footer>
    </div>
  );
}

export default App;
