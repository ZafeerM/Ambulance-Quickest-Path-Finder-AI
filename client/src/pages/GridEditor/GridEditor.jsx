import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../../context/AppContext';
import Grid from '../../components/Grid/Grid';
import Toolbar from '../../components/Toolbar/Toolbar';
import Button from '../../components/Button/Button';
import StepIndicator from '../../components/StepIndicator/StepIndicator';
import { validateGrid } from '../../utils/gridUtils';
import { CELL_TYPES } from '../../constants/cellTypes';
import AppHeader from '../../components/AppHeader/AppHeader';
import styles from './GridEditor.module.css';

export default function GridEditor() {
  const { grid, clearGrid, rows, cols } = useApp();
  const [activeTool, setActiveTool] = useState(CELL_TYPES.ROAD);
  const navigate = useNavigate();

  // Redirect to page 1 if the grid hasn't been initialised yet
  if (!grid) {
    navigate('/');
    return null;
  }

  const { hasStart, hasEnd, isValid } = validateGrid(grid);

  return (
    <div className={styles.page}>
      <div className={styles.blobA} aria-hidden="true" />
      <div className={styles.blobB} aria-hidden="true" />

      <div className={styles.inner}>
        <AppHeader />
        {/* ── Top bar ── */}
        <header className={styles.header}>
          <button className={styles.back} onClick={() => navigate('/')}>
            ← Back
          </button>
          <div className={styles.headerCenter}>
            <h1 className={styles.title}>Draw Your City Map</h1>
            <p className={styles.subtitle}>{rows} × {cols} grid</p>
          </div>
          <div className={styles.headerRight} />
        </header>

        <StepIndicator currentStep={1} />

        {/* ── Toolbar strip ── */}
        <div className={styles.toolbarStrip}>
          <Toolbar activeTool={activeTool} onToolChange={setActiveTool} />
          <Button variant="danger" size="sm" onClick={clearGrid}>
            🗑 Clear
          </Button>
        </div>

        {/* ── Grid ── */}
        <div className={styles.gridArea}>
          <Grid grid={grid} activeTool={activeTool} />
        </div>

        {/* ── Footer / validation ── */}
        <div className={styles.footer}>
          <div className={styles.chips}>
            <span className={`${styles.chip} ${hasStart ? styles.chipOk : styles.chipWarn}`}>
              {hasStart ? '✓' : '!'} Ambulance Start
            </span>
            <span className={`${styles.chip} ${hasEnd ? styles.chipOk : styles.chipWarn}`}>
              {hasEnd ? '✓' : '!'} Hospital End
            </span>
          </div>
          <Button size="lg" disabled={!isValid} onClick={() => navigate('/algorithm')}>
            Choose Algorithm →
          </Button>
        </div>
      </div>
    </div>
  );
}
