import React from 'react';
import { CELL_TYPES, CELL_ICONS } from '../../constants/cellTypes';
import styles from './Cell.module.css';
import wallImg    from '../../../assets/wall.jpg';
import roadImg    from '../../../assets/road.jpg';
import trafficImg from '../../../assets/traffic.jpg';

// Cells whose background is a full-cover image instead of a solid colour
const BG_IMAGES = {
  [CELL_TYPES.OBSTACLE]:     wallImg,
  [CELL_TYPES.ROAD]:         roadImg,
  [CELL_TYPES.ROAD_TRAFFIC]: trafficImg,
};

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

  const bgImg = BG_IMAGES[value];
  // Suppress emoji icons on cells that have a background image
  const icon = !bgImg ? CELL_ICONS[value] : null;

  return (
    <div
      className={`${styles.cell} ${typeClass} ${readOnly ? styles.readOnly : ''}`}
      style={{
        width: cellSize,
        height: cellSize,
        fontSize: cellSize * 0.48,
        ...(bgImg && { backgroundImage: `url(${bgImg})` }),
      }}
      onMouseDown={readOnly ? undefined : () => onMouseDown(row, col)}
      onMouseEnter={readOnly ? undefined : () => onMouseEnter(row, col)}
    >
      {icon && <span className={styles.icon}>{icon}</span>}
    </div>
  );
}
