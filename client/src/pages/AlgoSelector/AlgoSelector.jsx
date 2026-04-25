import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../../context/AppContext';
import Button from '../../components/Button/Button';
import StepIndicator from '../../components/StepIndicator/StepIndicator';
import {
  ALGORITHMS,
  ALGORITHM_LABELS,
  ALGORITHM_DESCRIPTIONS,
} from '../../constants/cellTypes';
import AppHeader from '../../components/AppHeader/AppHeader';
import styles from './AlgoSelector.module.css';

/* ── Per-algorithm accent colours ── */
const ALGO_META = {
  [ALGORITHMS.ASTAR]: {
    icon: '⭐',
    color: '#6c63ff',
    bg: 'rgba(108, 99, 255, 0.08)',
  },
  [ALGORITHMS.LOCAL_SEARCH]: {
    icon: '🔍',
    color: '#00b894',
    bg: 'rgba(0, 184, 148, 0.08)',
  },
  [ALGORITHMS.GENETIC]: {
    icon: '🧬',
    color: '#fd79a8',
    bg: 'rgba(253, 121, 168, 0.08)',
  },
};

/* ── Param panels ── */
function AStarParams({ params, onChange }) {
  const opts = ['manhattan', 'euclidean', 'diagonal'];
  return (
    <div className={styles.paramBody}>
      <p className={styles.paramLabel}>Heuristic Function</p>
      <div className={styles.radioRow}>
        {opts.map((h) => (
          <label
            key={h}
            className={`${styles.radioChip} ${params.heuristic === h ? styles.radioChipActive : ''}`}
          >
            <input
              type="radio"
              name="heuristic"
              value={h}
              checked={params.heuristic === h}
              onChange={() => onChange('heuristic', h)}
            />
            {h.charAt(0).toUpperCase() + h.slice(1)}
          </label>
        ))}
      </div>
    </div>
  );
}

function LocalParams({ params, onChange }) {
  return (
    <div className={styles.paramBody}>
      <p className={styles.paramLabel}>
        Max Iterations
        <span className={styles.paramValue}>{params.maxIterations.toLocaleString()}</span>
      </p>
      <input
        type="range"
        className={styles.range}
        min={100}
        max={10000}
        step={100}
        value={params.maxIterations}
        onChange={(e) => onChange('maxIterations', parseInt(e.target.value, 10))}
      />
    </div>
  );
}

function GeneticParams({ params, onChange }) {
  return (
    <div className={styles.paramBody}>
      <div className={styles.sliderRow}>
        <p className={styles.paramLabel}>
          Population Size
          <span className={styles.paramValue}>{params.populationSize}</span>
        </p>
        <input
          type="range"
          className={styles.range}
          min={10}
          max={500}
          step={10}
          value={params.populationSize}
          onChange={(e) => onChange('populationSize', parseInt(e.target.value, 10))}
        />
      </div>
      <div className={styles.sliderRow}>
        <p className={styles.paramLabel}>
          Generations
          <span className={styles.paramValue}>{params.generations}</span>
        </p>
        <input
          type="range"
          className={styles.range}
          min={10}
          max={1000}
          step={10}
          value={params.generations}
          onChange={(e) => onChange('generations', parseInt(e.target.value, 10))}
        />
      </div>
      <div className={styles.sliderRow}>
        <p className={styles.paramLabel}>
          Mutation Rate
          <span className={styles.paramValue}>
            {(params.mutationRate * 100).toFixed(0)}%
          </span>
        </p>
        <input
          type="range"
          className={styles.range}
          min={0.01}
          max={0.5}
          step={0.01}
          value={params.mutationRate}
          onChange={(e) => onChange('mutationRate', parseFloat(e.target.value))}
        />
      </div>
    </div>
  );
}

export default function AlgoSelector() {
  const { grid, rows, cols, selectedAlgo, algoParams, changeAlgo, updateParam } =
    useApp();
  const navigate = useNavigate();

  if (!grid) {
    navigate('/');
    return null;
  }

  const handleRun = () => {
    navigate('/visualizer');
  };

  return (
    <div className={styles.page}>
      <div className={styles.blobA} aria-hidden="true" />
      <div className={styles.blobB} aria-hidden="true" />

      <div className={styles.inner}>
        <AppHeader />
        {/* ── Header ── */}
        <header className={styles.header}>
          <button className={styles.back} onClick={() => navigate('/grid')}>
            ← Back
          </button>
          <div className={styles.headerCenter}>
            <h1 className={styles.title}>Pick Your Algorithm</h1>
            <p className={styles.subtitle}>Choose how to find the quickest path</p>
          </div>
          <div className={styles.headerRight} />
        </header>

        <StepIndicator currentStep={2} />

        {/* ── Algorithm cards ── */}
        <div className={styles.algoGrid}>
          {Object.values(ALGORITHMS).map((algo) => {
            const meta = ALGO_META[algo];
            const isSelected = selectedAlgo === algo;
            return (
              <button
                key={algo}
                className={`${styles.algoCard} ${isSelected ? styles.algoCardSelected : ''}`}
                style={
                  isSelected
                    ? { '--ac': meta.color, '--ab': meta.bg }
                    : {}
                }
                onClick={() => changeAlgo(algo)}
              >
                {isSelected && <div className={styles.selectedBadge}>✓</div>}
                <div className={styles.algoIcon}>{meta.icon}</div>
                <div className={styles.algoName}>{ALGORITHM_LABELS[algo]}</div>
                <div className={styles.algoDesc}>{ALGORITHM_DESCRIPTIONS[algo]}</div>
              </button>
            );
          })}
        </div>

        {/* ── Parameters panel ── */}
        <div
          className={styles.paramsPanel}
          style={{ '--ac': ALGO_META[selectedAlgo].color }}
        >
          <h2 className={styles.paramsTitle}>
            {ALGO_META[selectedAlgo].icon} {ALGORITHM_LABELS[selectedAlgo]} — Parameters
          </h2>
          {selectedAlgo === ALGORITHMS.ASTAR && (
            <AStarParams params={algoParams} onChange={updateParam} />
          )}
          {selectedAlgo === ALGORITHMS.LOCAL_SEARCH && (
            <LocalParams params={algoParams} onChange={updateParam} />
          )}
          {selectedAlgo === ALGORITHMS.GENETIC && (
            <GeneticParams params={algoParams} onChange={updateParam} />
          )}
        </div>

        {/* ── CTA ── */}
        <div className={styles.ctaRow}>
          <Button size="lg" onClick={handleRun}>
            🚑 Find the Path!
          </Button>
        </div>
      </div>
    </div>
  );
}
