import React from 'react';
import { CELL_TYPES, CELL_ICONS, CELL_COLORS } from '../../constants/cellTypes';
import styles from './Cell.module.css';

export default function Cell({ value, row, col, cellSize, onMouseDown, onMouseEnter }) {
  const typeClass = {
    [CELL_TYPES.ROAD]: styles.road,
    [CELL_TYPES.OBSTACLE]: styles.obstacle,
    [CELL_TYPES.START]: styles.start,
    [CELL_TYPES.END]: styles.end,
  }[value] ?? '';

  return (
    <div
      className={`${styles.cell} ${typeClass}`}
      style={{ width: cellSize, height: cellSize, fontSize: cellSize * 0.48 }}
      onMouseDown={() => onMouseDown(row, col)}
      onMouseEnter={() => onMouseEnter(row, col)}
    >
      {CELL_ICONS[value] && (
        <span className={styles.icon}>{CELL_ICONS[value]}</span>
      )}
    </div>
  );
}
