import React from 'react';
import styles from './AppHeader.module.css';

export default function AppHeader() {
  return (
    <div className={styles.brandBar}>
      <span className={styles.ambulanceIcon}>🚑</span>
      <div className={styles.brandText}>
        <span className={styles.brandTitle}>Ambulance Quickest Path Finder</span>
        <span className={styles.brandSub}>AI-Powered Emergency Routing</span>
      </div>
    </div>
  );
}
