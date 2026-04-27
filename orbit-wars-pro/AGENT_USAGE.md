# Orbit Wars Pro - Usage Guide

## Quick Start for Kaggle Competition

### 1. Using the Python Agent

```python
# agents/main_agent.py
from agents.main_agent import orbit_wars_agent

def your_agent(obs):
    return orbit_wars_agent(obs)
```

### 2. Strategy Modes

The agent supports 5 strategy modes:

| Strategy | Description | Best For |
|----------|-------------|----------|
| `adaptive` | Auto-selects based on game state (recommended) | General use |
| `greedy` | Prioritizes neutral capture | Early game, passive bots |
| `aggressive` | Targets enemy planets | Defensive opponents |
| `defensive` | Strengthens positions | Aggressive opponents |
| `hybrid` | Balanced approach | Mid-game transitions |

### 3. Direct Strategy Usage

```python
from agents.main_agent import greedy_agent, aggressive_agent, defensive_agent, hybrid_agent

def my_agent(obs):
    # Use specific strategy
    return greedy_agent(obs)  # or aggressive, defensive, hybrid
```

### 4. Advanced Usage with OrbitWarsPro Class

```python
from agents.main_agent import OrbitWarsPro

agent = OrbitWarsPro(strategy_mode='adaptive', debug=True)

def my_agent(obs):
    return agent.act(obs)
```

## Dashboard Usage

The interactive dashboard provides:

1. **Game Board Visualization**: See planets, fleets, and planned actions
2. **Statistics Panel**: Real-time game state analysis
3. **Strategy Selector**: Choose AI strategy mode
4. **Fleet Commander**: Plan and visualize fleet movements
5. **JSON Editor**: Paste Kaggle observations to visualize game states

### Loading Game States

1. Click "Load Example" to see sample game states
2. Or paste a Kaggle observation JSON in the editor
3. Click "Apply" to visualize the state

## Agent Architecture

```
agents/
├── main_agent.py           # Main orchestrator
├── strategies/
│   ├── greedy.py          # Neutral-focused expansion
│   ├── aggressive.py      # Enemy-targeting attacks
│   ├── defensive.py       # Position consolidation
│   └── hybrid.py          # Combined approach
└── utils/
    ├── game_analyzer.py   # State analysis & scoring
    ├── combat.py          # Combat resolution
    └── pathfinding.py     # Fleet trajectories
```

## Competition Submission

1. Copy `agents/main_agent.py` to your Kaggle submission
2. Use the `orbit_wars_agent` function as your main agent
3. For testing locally, use the dashboard to visualize gameplay

## Tips for Improvement

1. **Study opponent patterns** using the dashboard
2. **Tune strategy thresholds** in each strategy class
3. **Consider orbital mechanics** - some planets rotate
4. **Monitor the sun** - fleets crossing it are destroyed
5. **Fleet speed scales with size** - larger fleets travel faster
