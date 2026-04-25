import React, { useState, useRef } from 'react';
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
  const { grid, clearGrid, rows, cols, loadGrid } = useApp();
  const [activeTool, setActiveTool] = useState(CELL_TYPES.ROAD);
  const [loadError, setLoadError] = useState('');
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  const handleSave = () => {
    const json = JSON.stringify(grid);
    const blob = new Blob([json], { type: 'text/plain' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href     = url;
    a.download = 'map.txt';
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleLoadClick = () => {
    setLoadError('');
    fileInputRef.current.click();
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      try {
        const parsed = JSON.parse(ev.target.result);
        if (
          !Array.isArray(parsed) ||
          parsed.length === 0 ||
          !Array.isArray(parsed[0]) ||
          parsed[0].length === 0 ||
          !parsed.every((row) =>
            Array.isArray(row) && row.every((v) => Number.isInteger(v)),
          )
        ) {
          setLoadError('Invalid map file — could not read grid.');
          return;
        }
        loadGrid(parsed);
      } catch {
        setLoadError('Could not parse file. Make sure it\'s a saved map.');
      }
    };
    reader.readAsText(file);
    // Allow re-loading the same file
    e.target.value = '';
  };

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

          <div className={styles.footerActions}>
            <button className={styles.mapBtn} onClick={handleSave}>💾 Save Map</button>
            <button className={styles.mapBtn} onClick={handleLoadClick}>📂 Load Map</button>
            <input
              ref={fileInputRef}
              type="file"
              accept=".txt"
              style={{ display: 'none' }}
              onChange={handleFileChange}
            />
            {loadError && <span className={styles.loadError}>{loadError}</span>}
          </div>

          <Button size="lg" disabled={!isValid} onClick={() => navigate('/algorithm')}>
            Choose Algorithm →
          </Button>
        </div>
      </div>
    </div>
  );
}
