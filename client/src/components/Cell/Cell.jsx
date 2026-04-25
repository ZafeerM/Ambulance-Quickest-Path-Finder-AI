import React from 'react';
import { CELL_TYPES, CELL_ICONS } from '../../constants/cellTypes';
import styles from './Cell.module.css';

export default function Cell({
  value,
  row,
  col,
  cellSize,
  onMouseDown,
  onMouseEnter,
  readOnly = false,
}) {
  const typeClass = {
    [CELL_TYPES.ROAD]:         styles.road,
    [CELL_TYPES.OBSTACLE]:     styles.obstacle,
    [CELL_TYPES.START]:        styles.start,
    [CELL_TYPES.END]:          styles.end,
    [CELL_TYPES.ROAD_TRAFFIC]: styles.roadTraffic,
    [CELL_TYPES.VISITED]:      styles.visited,
    [CELL_TYPES.FRONTIER]:     styles.frontier,
    [CELL_TYPES.CURRENT]:      styles.current,
    [CELL_TYPES.PATH]:         styles.path,
  }[value] ?? '';

  return (
    <div
      className={`${styles.cell} ${typeClass} ${readOnly ? styles.readOnly : ''}`}
      style={{ width: cellSize, height: cellSize, fontSize: cellSize * 0.48 }}
      onMouseDown={readOnly ? undefined : () => onMouseDown(row, col)}
      onMouseEnter={readOnly ? undefined : () => onMouseEnter(row, col)}
    >
      {CELL_ICONS[value] && (
        <span className={styles.icon}>{CELL_ICONS[value]}</span>
      )}
    </div>
  );
}
