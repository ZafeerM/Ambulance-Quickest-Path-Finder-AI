import React, { createContext, useContext, useState, useCallback } from 'react';
import { createEmptyGrid, cloneGrid, findCell } from '../utils/gridUtils';
import { CELL_TYPES, ALGORITHMS, DEFAULT_ALGO_PARAMS } from '../constants/cellTypes';

const AppContext = createContext(null);

export function AppProvider({ children }) {
  const [rows, setRows] = useState(10);
  const [cols, setCols] = useState(10);
  const [grid, setGrid] = useState(null);
  const [selectedAlgo, setSelectedAlgo] = useState(ALGORITHMS.ASTAR);
  const [algoParams, setAlgoParams] = useState(DEFAULT_ALGO_PARAMS[ALGORITHMS.ASTAR]);

  /** Initialise (or reset) the grid to rows×cols of EMPTY cells */
  const initGrid = useCallback((r, c) => {
    setRows(r);
    setCols(c);
    setGrid(createEmptyGrid(r, c));
  }, []);

  /** Paint a single cell; enforces at most one START and one END */
  const setCell = useCallback((row, col, type) => {
    setGrid((prev) => {
      const next = cloneGrid(prev);

      if (type === CELL_TYPES.START) {
        const existing = findCell(next, CELL_TYPES.START);
        if (existing) next[existing.row][existing.col] = CELL_TYPES.EMPTY;
      }
      if (type === CELL_TYPES.END) {
        const existing = findCell(next, CELL_TYPES.END);
        if (existing) next[existing.row][existing.col] = CELL_TYPES.EMPTY;
      }

      next[row][col] = type;
      return next;
    });
  }, []);

  /** Reset every cell back to EMPTY */
  const clearGrid = useCallback(() => {
    setGrid(createEmptyGrid(rows, cols));
  }, [rows, cols]);

  /** Switch algorithm and reset params to their defaults */
  const changeAlgo = useCallback((algo) => {
    setSelectedAlgo(algo);
    setAlgoParams(DEFAULT_ALGO_PARAMS[algo]);
  }, []);

  /** Update a single parameter key for the current algorithm */
  const updateParam = useCallback((key, value) => {
    setAlgoParams((prev) => ({ ...prev, [key]: value }));
  }, []);

  return (
    <AppContext.Provider
      value={{
        rows,
        cols,
        grid,
        setCell,
        clearGrid,
        initGrid,
        selectedAlgo,
        algoParams,
        changeAlgo,
        updateParam,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be used inside <AppProvider>');
  return ctx;
}
