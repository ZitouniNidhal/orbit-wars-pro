import React from 'react';

export type StrategyMode = 'greedy' | 'aggressive' | 'defensive' | 'hybrid' | 'adaptive';

interface StrategySelectorProps {
  selectedStrategy: StrategyMode;
  onStrategyChange: (strategy: StrategyMode) => void;
}

const strategies: { id: StrategyMode; name: string; description: string; icon: string }[] = [
  {
    id: 'adaptive',
    name: 'Adaptive',
    description: 'Automatically selects best strategy based on game state',
    icon: '🧠',
  },
  {
    id: 'greedy',
    name: 'Greedy',
    description: 'Prioritizes neutral planet capture and resources',
    icon: '🎯',
  },
  {
    id: 'aggressive',
    name: 'Aggressive',
    description: 'Focuses on attacking enemy planets',
    icon: '⚔️',
  },
  {
    id: 'defensive',
    name: 'Defensive',
    description: 'Consolidates positions and defends against attacks',
    icon: '🛡️',
  },
  {
    id: 'hybrid',
    name: 'Hybrid',
    description: 'Balanced approach mixing offense and defense',
    icon: '⚖️',
  },
];

const StrategySelector: React.FC<StrategySelectorProps> = ({
  selectedStrategy,
  onStrategyChange,
}) => {
  return (
    <div className="bg-gray-900 rounded-lg p-4">
      <h2 className="text-lg font-bold text-white border-b border-gray-700 pb-2 mb-4">
        Strategy Mode
      </h2>
      <div className="space-y-2">
        {strategies.map((strategy) => (
          <button
            key={strategy.id}
            onClick={() => onStrategyChange(strategy.id)}
            className={`w-full text-left p-3 rounded-lg transition-all ${
              selectedStrategy === strategy.id
                ? 'bg-purple-900/50 border-2 border-purple-500'
                : 'bg-gray-800 border-2 border-transparent hover:bg-gray-750'
            }`}
          >
            <div className="flex items-center gap-3">
              <span className="text-2xl">{strategy.icon}</span>
              <div>
                <div className="font-semibold text-white">{strategy.name}</div>
                <div className="text-xs text-gray-400">{strategy.description}</div>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};

export default StrategySelector;
