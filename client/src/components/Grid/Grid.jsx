import React from 'react';
import Cell from '../Cell/Cell';
import { useGridInteraction } from '../../hooks/useGridInteraction';
import styles from './Grid.module.css';

export default function Grid({ grid, activeTool }) {
  const { handleMouseDown, handleMouseEnter } = useGridInteraction(activeTool);

  const rows = grid.length;
  const cols = grid[0]?.length ?? 0;

  // Fit cells inside a 640 px square; clamp between 22 px and 52 px
  const cellSize = Math.max(22, Math.min(52, Math.floor(640 / Math.max(rows, cols))));

  return (
    <div className={styles.wrapper}>
      <div
        className={styles.grid}
        style={{ gridTemplateColumns: `repeat(${cols}, ${cellSize}px)` }}
        onDragStart={(e) => e.preventDefault()}
      >
        {grid.map((row, r) =>
          row.map((cell, c) => (
            <Cell
              key={`${r}-${c}`}
              value={cell}
              row={r}
              col={c}
              cellSize={cellSize}
              onMouseDown={handleMouseDown}
              onMouseEnter={handleMouseEnter}
            />
          )),
        )}
      </div>
    </div>
  );
}
