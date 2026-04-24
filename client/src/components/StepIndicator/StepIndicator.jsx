import React from 'react';
import styles from './StepIndicator.module.css';

const STEPS = [
  { label: 'Map Size', icon: '📐' },
  { label: 'Draw Map', icon: '🗺️' },
  { label: 'Algorithm', icon: '🧠' },
];

export default function StepIndicator({ currentStep }) {
  return (
    <div className={styles.container}>
      {STEPS.map((step, idx) => (
        <React.Fragment key={idx}>
          <div
            className={[
              styles.step,
              idx === currentStep ? styles.active : '',
              idx < currentStep ? styles.done : '',
            ]
              .filter(Boolean)
              .join(' ')}
          >
            <div className={styles.circle}>
              {idx < currentStep ? '✓' : step.icon}
            </div>
            <span className={styles.label}>{step.label}</span>
          </div>

          {idx < STEPS.length - 1 && (
            <div
              className={[
                styles.connector,
                idx < currentStep ? styles.connectorDone : '',
              ]
                .filter(Boolean)
                .join(' ')}
            />
          )}
        </React.Fragment>
      ))}
    </div>
  );
}
