import React, { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../../context/AppContext';
import { usePathfinder } from '../../hooks/usePathfinder';
import { CELL_TYPES, CELL_COLORS, ALGORITHM_LABELS } from '../../constants/cellTypes';
import AppHeader from '../../components/AppHeader/AppHeader';
import Grid from '../../components/Grid/Grid';
import styles from './Visualizer.module.css';

const LEGEND_ITEMS = [
  { type: CELL_TYPES.START, label: 'Ambulance (Start)' },
  { type: CELL_TYPES.END, label: 'Hospital (End)' },
  { type: CELL_TYPES.ROAD, label: 'Road' },
  { type: CELL_TYPES.OBSTACLE, label: 'Wall' },
  { type: CELL_TYPES.CURRENT, label: 'Current node' },
  { type: CELL_TYPES.FRONTIER, label: 'Frontier (open set)' },
  { type: CELL_TYPES.VISITED, label: 'Visited (closed)' },
  { type: CELL_TYPES.PATH, label: 'Shortest path' },
];

const SWATCH_TEXT = {
  [CELL_TYPES.START]: 'S',
  [CELL_TYPES.END]: 'E',
  [CELL_TYPES.ROAD]: null,
  [CELL_TYPES.OBSTACLE]: null,
  [CELL_TYPES.CURRENT]: 'C',
  [CELL_TYPES.FRONTIER]: 'F',
  [CELL_TYPES.VISITED]: 'V',
  [CELL_TYPES.PATH]: 'P',
};

const STATUS_LABELS = {
  idle: 'Idle',
  connecting: 'Connecting...',
  receiving: 'Buffering...',
  done: 'Done',
  error: 'Error',
};

const STATUS_CLASS = {
  idle: styles.badgeIdle,
  connecting: styles.badgeConnecting,
  receiving: styles.badgeReceiving,
  done: styles.badgeDone,
  error: styles.badgeError,
};

export default function Visualizer() {
  const navigate = useNavigate();
  const { grid, rows, cols, selectedAlgo, algoParams } = useApp();
  const {
    status,
    currentGrid,
    messages,
    playIndex,
    totalFrames,
    isPlaying,
    speed,
    errorMsg,
    startRun,
    play,
    pause,
    stepForward,
    stepBackward,
    goToStep,
    changeSpeed,
  } = usePathfinder();
  const logRef = useRef(null);

  useEffect(() => {
    if (!grid || grid.length === 0) navigate('/');
  }, [grid, navigate]);

  useEffect(() => {
    if (grid && grid.length > 0) {
      startRun(grid, rows, cols, selectedAlgo, algoParams);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [messages.length]);

  const displayGrid = currentGrid ?? grid;
  const atEnd = totalFrames > 0 && playIndex >= totalFrames - 1;
  const atStart = playIndex <= 0;
  const isTerminal = status === 'done' || status === 'error';

  return (
    <div className={styles.page}>
      <div className={styles.blobA} aria-hidden="true" />
      <div className={styles.blobB} aria-hidden="true" />

      <div className={styles.inner}>
        <AppHeader />

        <div className={styles.stage}>
          <div className={styles.topBar}>
            <button className={styles.backBtn} onClick={() => navigate('/algorithm')}>
              {'<-'} Try Again
            </button>
            <div className={styles.algoLabel}>
              {ALGORITHM_LABELS[selectedAlgo] ?? selectedAlgo}
            </div>
            <span className={`${styles.badge} ${STATUS_CLASS[status] ?? ''}`}>
              {STATUS_LABELS[status] ?? status}
            </span>
          </div>

          <div className={styles.controls}>
            <span className={styles.stepCounter}>
              {totalFrames === 0
                ? 'Waiting...'
                : `Step ${playIndex + 1} / ${totalFrames}${!isTerminal ? '+' : ''}`}
            </span>

            <button className={styles.ctrlBtn} onClick={stepBackward} disabled={atStart} title="Step back">
              {'<<'} Back
            </button>

            {isPlaying ? (
              <button className={`${styles.ctrlBtn} ${styles.ctrlPrimary}`} onClick={pause} title="Pause">
                Pause
              </button>
            ) : (
              <button
                className={`${styles.ctrlBtn} ${styles.ctrlPrimary}`}
                onClick={play}
                disabled={atEnd && isTerminal}
                title="Play"
              >
                Play
              </button>
            )}

            <button
              className={styles.ctrlBtn}
              onClick={stepForward}
              disabled={atEnd && isTerminal}
              title="Step forward"
            >
              Next {'>>'}
            </button>

            <div className={styles.speedGroup}>
              {['slow', 'normal', 'fast'].map((s) => (
                <button
                  key={s}
                  className={`${styles.speedBtn} ${speed === s ? styles.speedActive : ''}`}
                  onClick={() => changeSpeed(s)}
                >
                  {s.charAt(0).toUpperCase() + s.slice(1)}
                </button>
              ))}
            </div>
          </div>

          <div className={styles.scrubberWrap}>
            <input
              className={styles.scrubber}
              type="range"
              min={0}
              max={Math.max(totalFrames - 1, 0)}
              value={Math.max(playIndex, 0)}
              onChange={(e) => goToStep(parseInt(e.target.value, 10))}
              disabled={totalFrames === 0}
            />
          </div>

          <div className={styles.content}>
            <div className={styles.gridPanel}>
              {displayGrid && displayGrid.length > 0 && <Grid grid={displayGrid} readOnly={true} />}
            </div>

            <div className={styles.sidebar}>
              <section className={styles.legend}>
                <h3 className={styles.sideTitle}>Legend</h3>
                {LEGEND_ITEMS.map(({ type, label }) => (
                  <div key={type} className={styles.legendItem}>
                    <span className={styles.legendSwatch} style={{ background: CELL_COLORS[type] }}>
                      {SWATCH_TEXT[type]}
                    </span>
                    <span className={styles.legendLabel}>{label}</span>
                  </div>
                ))}
              </section>

              <section className={styles.logSection}>
                <h3 className={styles.sideTitle}>
                  AI Log
                  <span className={styles.logCount}>{messages.length > 0 ? ` (${messages.length})` : ''}</span>
                </h3>
                <div className={styles.logScroll} ref={logRef}>
                  {messages.length === 0 ? (
                    <p className={styles.logEmpty}>Waiting for server...</p>
                  ) : (
                    messages.map((m, i) => (
                      <p
                        key={i}
                        className={`${styles.logLine} ${
                          m.type === 'done'
                            ? styles.logDone
                            : m.type === 'error'
                              ? styles.logError
                              : i === messages.length - 1
                                ? styles.logLatest
                                : ''
                        }`}
                      >
                        <span className={styles.logIdx}>{i + 1}.</span> {m.text}
                      </p>
                    ))
                  )}
                </div>
              </section>

              {status === 'error' && errorMsg && <div className={styles.errorBox}>{errorMsg}</div>}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
