import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../../context/AppContext';
import Button from '../../components/Button/Button';
import StepIndicator from '../../components/StepIndicator/StepIndicator';
import { GRID_MIN, GRID_MAX } from '../../constants/cellTypes';
import AppHeader from '../../components/AppHeader/AppHeader';
import styles from './MapSetup.module.css';

function clamp(val) {
  const n = parseInt(val, 10);
  if (isNaN(n)) return GRID_MIN;
  return Math.min(GRID_MAX, Math.max(GRID_MIN, n));
}

export default function MapSetup() {
  const { initGrid, rows: savedRows, cols: savedCols } = useApp();
  const [rows, setRows] = useState(savedRows);
  const [cols, setCols] = useState(savedCols);
  const navigate = useNavigate();

  const handleNext = () => {
    initGrid(rows, cols);
    navigate('/grid');
  };

  const previewRows = Math.min(rows, 10);
  const previewCols = Math.min(cols, 14);

  return (
    <div className={styles.page}>
      {/* Decorative blobs */}
      <div className={styles.blobA} aria-hidden="true" />
      <div className={styles.blobB} aria-hidden="true" />

      <div className={styles.inner}>
        <AppHeader />
        <header className={styles.header}>
          <h1 className={styles.title}>Design Your City</h1>
          <p className={styles.subtitle}>Set the grid dimensions to get started</p>
        </header>

        <StepIndicator currentStep={0} />

        <div className={styles.card}>
          {/* Rows input */}
          <div className={styles.field}>
            <label className={styles.fieldLabel}>
              <span className={styles.fieldIcon}>↕</span>
              Rows
            </label>
            <div className={styles.inputRow}>
              <button
                className={styles.stepper}
                onClick={() => setRows((r) => Math.max(GRID_MIN, r - 1))}
              >
                −
              </button>
              <input
                type="number"
                className={styles.numInput}
                value={rows}
                min={GRID_MIN}
                max={GRID_MAX}
                onChange={(e) => setRows(clamp(e.target.value))}
              />
              <button
                className={styles.stepper}
                onClick={() => setRows((r) => Math.min(GRID_MAX, r + 1))}
              >
                +
              </button>
            </div>
          </div>

          <div className={styles.divider} />

          {/* Cols input */}
          <div className={styles.field}>
            <label className={styles.fieldLabel}>
              <span className={styles.fieldIcon}>↔</span>
              Columns
            </label>
            <div className={styles.inputRow}>
              <button
                className={styles.stepper}
                onClick={() => setCols((c) => Math.max(GRID_MIN, c - 1))}
              >
                −
              </button>
              <input
                type="number"
                className={styles.numInput}
                value={cols}
                min={GRID_MIN}
                max={GRID_MAX}
                onChange={(e) => setCols(clamp(e.target.value))}
              />
              <button
                className={styles.stepper}
                onClick={() => setCols((c) => Math.min(GRID_MAX, c + 1))}
              >
                +
              </button>
            </div>
          </div>

          {/* Live mini-preview */}
          <div className={styles.preview}>
            <span className={styles.previewLabel}>
              {rows} × {cols} = {rows * cols} cells
            </span>
            <div
              className={styles.miniGrid}
              style={{ gridTemplateColumns: `repeat(${previewCols}, 1fr)` }}
            >
              {Array.from({ length: previewRows * previewCols }).map((_, i) => (
                <div key={i} className={styles.miniCell} />
              ))}
            </div>
            {(rows > 10 || cols > 14) && (
              <p className={styles.previewNote}>Preview truncated</p>
            )}
          </div>

          <Button fullWidth size="lg" onClick={handleNext}>
            Build My Map →
          </Button>
        </div>
      </div>
    </div>
  );
}
