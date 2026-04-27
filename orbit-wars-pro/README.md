# Orbit Wars Pro - Competitive AI Agent

## Overview

Orbit Wars Pro is a sophisticated multi-strategy AI agent designed for the Planet Wars-style competition. The agent combines multiple game phases and strategies to adapt to different opponent playstyles and game states.

## Features

- **Multi-Strategy Architecture**: Switches between Greedy, Aggressive, Defensive, and Hybrid modes based on game state
- **Orbital Mechanics Awareness**: Accounts for rotating planets when planning fleet movements
- **Combat Optimization**: Uses weighted scoring to prioritize high-value targets
- **Early/Mid/Late Game Logic**: Different strategies for each phase of the game
- **Interactive Dashboard**: Visualize game state and agent decisions in real-time

## Quick Start

### Option 1: Direct Python Agent

```python
from agents.main_agent import orbit_wars_agent

def your_agent(obs):
    return orbit_wars_agent(obs)
```

### Option 2: Using the Framework

```python
from agents.main_agent import OrbitWarsPro

agent = OrbitWarsPro()
agent.set_strategy('aggressive')

def your_agent(obs):
    return agent.act(obs)
```

## Strategy Modes

| Mode | Description | Best Against |
|------|-------------|--------------|
| `greedy` | Prioritizes neutral planet capture | Passive bots |
| `aggressive` | Targets enemy planets aggressively | Defensive bots |
| `defensive` | Strengthens positions before expanding | Aggressive bots |
| `hybrid` | Balances offense and defense | General use |
| `adaptive` | Automatically selects based on game state | Unknown opponents |

## Game Rules Summary

- **Objective**: Control the most ships (planets + fleets) at game end
- **Board**: 100x100 space with sun at center (destroys crossing fleets)
- **Planets**: Produce 1-5 ships/turn, some orbit the sun
- **Fleets**: Speed scales with size (1-6 units/turn)
- **Turns**: Max 500 turns or last player standing

## Project Structure

```
orbit-wars-pro/
├── agents/
│   ├── main_agent.py          # Main orchestrator
│   ├── strategies/
│   │   ├── greedy.py         # Neutral-focused strategy
│   │   ├── aggressive.py     # Enemy-targeting strategy
│   │   ├── defensive.py      # Position-strengthening strategy
│   │   └── hybrid.py         # Combined approach
│   └── utils/
│       ├── game_analyzer.py   # State analysis utilities
│       ├── combat.py          # Combat resolution
│       └── pathfinding.py     # Fleet trajectory calculation
├── dashboard/                 # React visualization app
├── docs/                      # Additional documentation
└── tests/                     # Unit tests
```

## Competition Timeline

| Date | Event |
|------|-------|
| April 16, 2026 | Start Date |
| June 16, 2026 | Entry Deadline |
| June 23, 2026 | Final Submission |
| July 8, 2026 | Final Evaluation Complete |

## Prizes

- **1st-10th Place**: $5,000 each
- **Total Prize Pool**: $50,000

## License

MIT License - Free to use and modify for the competition.

---

**Author**: MiniMax Agent
**Version**: 1.0.0
