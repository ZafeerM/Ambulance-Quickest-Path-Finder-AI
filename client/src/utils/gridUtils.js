import { CELL_TYPES } from '../constants/cellTypes';

/** Create a rows×cols 2D array filled with EMPTY (0) */
export function createEmptyGrid(rows, cols) {
  return Array.from({ length: rows }, () => Array(cols).fill(CELL_TYPES.EMPTY));
}

/** Shallow-clone a 2D grid (rows are new arrays, values are primitives) */
export function cloneGrid(grid) {
  return grid.map((row) => [...row]);
}

/** Find the first cell matching a given type; returns { row, col } or null */
export function findCell(grid, type) {
  for (let r = 0; r < grid.length; r++) {
    for (let c = 0; c < grid[r].length; c++) {
      if (grid[r][c] === type) return { row: r, col: c };
    }
  }
  return null;
}

/** Check whether the grid has both a START and an END cell */
export function validateGrid(grid) {
  const hasStart = grid.some((row) => row.includes(CELL_TYPES.START));
  const hasEnd = grid.some((row) => row.includes(CELL_TYPES.END));
  return { hasStart, hasEnd, isValid: hasStart && hasEnd };
}

/** Build the JSON payload that will be sent to the backend */
export function gridToPayload(grid, rows, cols, algorithm, algoParams) {
  return {
    grid,
    rows,
    cols,
    algorithm,
    params: algoParams,
  };
}
