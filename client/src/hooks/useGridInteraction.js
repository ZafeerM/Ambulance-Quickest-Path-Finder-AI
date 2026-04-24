import { useRef, useCallback, useEffect } from 'react';
import { useApp } from '../context/AppContext';

/**
 * Handles click-and-drag painting on the grid.
 * Pass the currently active tool (CELL_TYPES value) and it returns
 * event handlers to spread onto each Cell.
 */
export function useGridInteraction(activeTool) {
  const { setCell } = useApp();
  const isDrawing = useRef(false);

  const handleMouseDown = useCallback(
    (row, col) => {
      isDrawing.current = true;
      setCell(row, col, activeTool);
    },
    [activeTool, setCell],
  );

  const handleMouseEnter = useCallback(
    (row, col) => {
      if (!isDrawing.current) return;
      setCell(row, col, activeTool);
    },
    [activeTool, setCell],
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
