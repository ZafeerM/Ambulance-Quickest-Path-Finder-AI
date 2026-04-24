import React from 'react';
import { CELL_TYPES, CELL_LABELS, CELL_ICONS, TOOL_COLORS } from '../../constants/cellTypes';
import styles from './Toolbar.module.css';

const TOOLS = [
  CELL_TYPES.ROAD,
  CELL_TYPES.OBSTACLE,
  CELL_TYPES.START,
  CELL_TYPES.END,
  CELL_TYPES.EMPTY,   // last = eraser
];

export default function Toolbar({ activeTool, onToolChange }) {
  return (
    <div className={styles.toolbar}>
      <span className={styles.brushLabel}>Brush</span>
      <div className={styles.tools}>
        {TOOLS.map((tool) => {
          const isActive = activeTool === tool;
          const color = TOOL_COLORS[tool];
          return (
            <button
              key={tool}
              className={`${styles.tool} ${isActive ? styles.toolActive : ''}`}
              style={{
                '--tc': color,
              }}
              onClick={() => onToolChange(tool)}
              title={CELL_LABELS[tool]}
            >
              <span className={styles.toolIcon}>{CELL_ICONS[tool] ?? '✕'}</span>
              <span className={styles.toolName}>{CELL_LABELS[tool]}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
