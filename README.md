# Ambulance Quickest Path Finder — AI Pathfinding Visualizer

An interactive web application that lets you draw a custom city grid and watch three AI algorithms race to find the quickest route from an ambulance to a hospital — visualised step by step in real time.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Algorithms](#algorithms)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Windows Setup](#windows-setup)
  - [macOS / Linux Setup](#macos--linux-setup)
- [Configuration](#configuration)
- [Author](#author)

---

## Overview

The app walks you through a four-step flow:

1. **Map Setup** — choose your grid size (5×5 up to 40×40)
2. **Grid Editor** — paint the city: place roads, walls, traffic jams, the ambulance, and the hospital
3. **Algorithm Selector** — pick an algorithm and tune its parameters
4. **Visualizer** — watch the algorithm explore the grid live, then see the optimal path highlighted

All pathfinding runs on a Python backend streamed over WebSocket, so the frontend receives and displays every single step as it is computed.

---

## Features

| Feature | Details |
|---|---|
| Custom grid drawing | Paint roads, walls, traffic cells, ambulance start, and hospital end with click-and-drag |
| Weighted terrain | Roads cost 1, traffic cells cost 3 — algorithms find the cheapest route, not just the shortest |
| Grid sizes | 5×5 minimum up to 40×40 maximum |
| Three AI algorithms | A\*, Hill Climbing (local search), Genetic Algorithm |
| Real-time step streaming | Every exploration step is streamed over WebSocket and buffered client-side |
| Playback controls | Play, pause, step forward, step backward, jump to any frame |
| Playback speed | Slow (600 ms/step), Normal (250 ms/step), Fast (80 ms/step) |
| Visual overlays | Explored cells (cyan), frontier cells (orange), current node (purple), final path (pink) |
| Per-algorithm messages | Each frame includes a detailed log message describing what the algorithm is doing |

---

## Algorithms

### A* Search
Classic informed search using a heuristic to guide exploration toward the goal. Three heuristics are available:

- **Manhattan** — sum of horizontal + vertical distance (default)
- **Euclidean** — straight-line distance
- **Diagonal (Chebyshev)** — allows diagonal distance measurement

Guarantees the optimal (lowest-cost) path when the heuristic is admissible. Visualises the open/closed sets expanding across the grid.

### Hill Climbing (Local Search)
A local search algorithm that starts from an initial BFS path and iteratively improves it by replacing sub-segments with cheaper alternatives (segment-replacement neighbourhood). On getting stuck at a local optimum it performs a random restart using randomised BFS to explore a completely different area of the search space. Tracks the global best path across all restarts.

### Genetic Algorithm
Evolutionary algorithm that maintains a population of complete paths:

1. **Initialise** — build a diverse population of random paths (shown one by one on screen)
2. **Evaluate** — score every path by total traversal cost
3. **Select** — keep the top 50% as parents
4. **Crossover** — splice two parent paths at a shared intermediate cell
5. **Mutate** — re-route a random sub-segment with a configurable probability
6. **Repeat** for all generations, tracking the best-ever path

During evolution the population cloud (grey → orange convergence heat) is shown each generation. The best path is only revealed at the end.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, React Router v6, Vite 5 |
| Backend | Python 3.11+, FastAPI, Uvicorn |
| Communication | WebSocket (native browser API + FastAPI WebSocket) |
| Validation | Pydantic v2 |
| Styling | CSS Modules |

---

## Project Structure

```
├── client/                  # React frontend (Vite)
│   └── src/
│       ├── pages/           # MapSetup, GridEditor, AlgoSelector, Visualizer
│       ├── components/      # Grid, Cell, Toolbar, Button, AppHeader, StepIndicator
│       ├── hooks/           # usePathfinder (WebSocket + playback), useGridInteraction
│       ├── context/         # AppContext (shared grid + algorithm state)
│       ├── constants/       # Cell types, colours, algorithm names
│       └── config/          # API base URL
│
└── server/                  # FastAPI backend
    ├── main.py              # WebSocket endpoint (/ws/applyAI)
    ├── config.py            # Settings (CORS origins, delays)
    ├── schemas.py           # Pydantic request/response models
    └── services/
        ├── astar.py         # A* pathfinding generator
        ├── hill_climbing.py # Hill climbing + random restart generator
        └── genetic.py       # Genetic algorithm generator
```

---

## Getting Started

### Prerequisites

Make sure you have the following installed:

| Tool | Minimum version | Download |
|---|---|---|
| Python | 3.11 | https://www.python.org/downloads/ |
| Node.js | 18 | https://nodejs.org/ |
| npm | 9 (bundled with Node.js) | — |

---

### Windows Setup

Open **PowerShell** or **Command Prompt** in the project root.

#### 1. Start the backend

```powershell
cd server

# Create a virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# (Optional) copy the example env file
copy .env.example .env

# Start the server
uvicorn main:app --reload --port 8000
```

> If you get a script execution policy error, run:
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

The backend will be running at `http://localhost:8000`.

#### 2. Start the frontend

Open a **second** PowerShell window in the project root:

```powershell
cd client

npm install
npm run dev
```

Open your browser at **http://localhost:3000**.

---

### macOS / Linux Setup

Open two terminal windows in the project root.

#### 1. Start the backend (Terminal 1)

```bash
cd server

# Create a virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# (Optional) copy the example env file
cp .env.example .env

# Start the server
uvicorn main:app --reload --port 8000
```

The backend will be running at `http://localhost:8000`.

#### 2. Start the frontend (Terminal 2)

```bash
cd client

npm install
npm run dev
```

Open your browser at **http://localhost:3000**.

---

## Configuration

The backend reads settings from `server/.env`. Copy `server/.env.example` to `server/.env` to customise:

| Variable | Default | Description |
|---|---|---|
| `STEP_DELAY_SECONDS` | `0.1` | Seconds between each streamed step (set to `0` to disable) |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed frontend origins (JSON array) |

The frontend API URL is set in `client/src/config/api.js` and points to `ws://localhost:8000` by default.

---

## Author

**Zafeer Mahmood**
Email: zafeermahmood04@gmail.com
