// Cell type values stored in the 2D grid array
export const CELL_TYPES = Object.freeze({
  EMPTY: 0,
  ROAD: 1,
  OBSTACLE: 2,
  START: 3,
  END: 4,
});

// Human-readable label for each tool in the toolbar
export const CELL_LABELS = Object.freeze({
  [CELL_TYPES.EMPTY]: 'Erase',
  [CELL_TYPES.ROAD]: 'Road',
  [CELL_TYPES.OBSTACLE]: 'Wall',
  [CELL_TYPES.START]: 'Ambulance',
  [CELL_TYPES.END]: 'Hospital',
});

// Emoji icons rendered inside each cell
export const CELL_ICONS = Object.freeze({
  [CELL_TYPES.EMPTY]: null,
  [CELL_TYPES.ROAD]: '🛣️',
  [CELL_TYPES.OBSTACLE]: '🧱',
  [CELL_TYPES.START]: '🚑',
  [CELL_TYPES.END]: '🏥',
});

// Background colors for each cell type
export const CELL_COLORS = Object.freeze({
  [CELL_TYPES.EMPTY]: '#f1f3f5',
  [CELL_TYPES.ROAD]: '#74b9ff',
  [CELL_TYPES.OBSTACLE]: '#2d3436',
  [CELL_TYPES.START]: '#00b894',
  [CELL_TYPES.END]: '#e17055',
});

// Color used in the toolbar button for each tool
export const TOOL_COLORS = Object.freeze({
  [CELL_TYPES.EMPTY]: '#ff7675',
  [CELL_TYPES.ROAD]: '#74b9ff',
  [CELL_TYPES.OBSTACLE]: '#636e72',
  [CELL_TYPES.START]: '#00b894',
  [CELL_TYPES.END]: '#e17055',
});

// Algorithm identifiers sent to the backend
export const ALGORITHMS = Object.freeze({
  ASTAR: 'astar',
  LOCAL_SEARCH: 'local_search',
  GENETIC: 'genetic',
});

export const ALGORITHM_LABELS = Object.freeze({
  [ALGORITHMS.ASTAR]: 'A* Search',
  [ALGORITHMS.LOCAL_SEARCH]: 'Local Search',
  [ALGORITHMS.GENETIC]: 'Genetic Algorithm',
});

export const ALGORITHM_DESCRIPTIONS = Object.freeze({
  [ALGORITHMS.ASTAR]:
    'Optimal pathfinding using heuristics. Guaranteed to find the shortest path.',
  [ALGORITHMS.LOCAL_SEARCH]:
    'Iterative improvement strategy. Fast but may settle for a local optimum.',
  [ALGORITHMS.GENETIC]:
    'Evolutionary approach inspired by natural selection. Great for complex maps.',
});

// Default parameter values for each algorithm
export const DEFAULT_ALGO_PARAMS = Object.freeze({
  [ALGORITHMS.ASTAR]: {
    heuristic: 'manhattan',
  },
  [ALGORITHMS.LOCAL_SEARCH]: {
    maxIterations: 1000,
  },
  [ALGORITHMS.GENETIC]: {
    populationSize: 100,
    generations: 200,
    mutationRate: 0.05,
  },
});

// Grid size constraints
export const GRID_MIN = 3;
export const GRID_MAX = 40;
