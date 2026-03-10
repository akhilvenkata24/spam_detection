import { useState } from 'react';
import styles from './Dashboard.module.css';

export function Settings() {
    const [threshold, setThreshold] = useState(60);

    return (
        <div className={styles.settingsCard}>
            <h3 className={styles.sectionTitle}>Analysis Configuration</h3>

            <div className={styles.settingsGroup}>
                <div>
                    <div className={styles.sliderHeader}>
                        <label className={styles.sliderLabel}>Spam Storage Threshold</label>
                        <span className={styles.sliderValue}>{threshold}%</span>
                    </div>
                    <input
                        type="range"
                        min="0"
                        max="100"
                        value={threshold}
                        onChange={(e) => setThreshold(e.target.value)}
                        className={styles.rangeInput}
                    />
                    <p className={styles.settingDesc}>
                        Only save messages to the database if the risk score is above <span style={{ fontWeight: 'bold', color: 'var(--foreground)' }}>{threshold}%</span>.
                        Low-risk messages will be discarded after analysis to save space.
                    </p>
                </div>

                <div className={styles.toggleRow}>
                    <span className={styles.sliderLabel}>Auto-Flag Malicious Links</span>
                    <label className={styles.toggleSwitch}>
                        <input type="checkbox" className={styles.toggleInput} />
                        <span className={styles.toggleSlider}></span>
                    </label>
                </div>
            </div>
        </div>
    )
}
