import { useRef, useCallback, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import { CELL_TYPES } from '../constants/cellTypes';

/**
 * Handles click-and-drag painting on the grid.
 * Pass the currently active tool (CELL_TYPES value) and it returns
 * event handlers to spread onto each Cell.
 *
 * The Erase tool (CELL_TYPES.EMPTY) maps to OBSTACLE — there is no empty
 * space; erasing a cell reverts it to a wall.
 */
export function useGridInteraction(activeTool) {
  const { setCell } = useApp();
  const isDrawing = useRef(false);

  // Erase (EMPTY) reverts cells to wall — no empty space is ever created
  const effectiveTool =
    activeTool === CELL_TYPES.EMPTY ? CELL_TYPES.OBSTACLE : activeTool;

  const handleMouseDown = useCallback(
    (row, col) => {
      isDrawing.current = true;
      setCell(row, col, effectiveTool);
    },
    [effectiveTool, setCell],
  );

  const handleMouseEnter = useCallback(
    (row, col) => {
      if (!isDrawing.current) return;
      setCell(row, col, effectiveTool);
    },
    [effectiveTool, setCell],
  );

  // Stop drawing when the mouse is released anywhere on the page
  useEffect(() => {
    const stop = () => {
      isDrawing.current = false;
    };
    window.addEventListener('mouseup', stop);
    return () => window.removeEventListener('mouseup', stop);
  }, []);

  return { handleMouseDown, handleMouseEnter };
}
