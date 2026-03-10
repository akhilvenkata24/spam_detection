import styles from './RiskMeter.module.css';

export function RiskMeter({ score }) {
    // Score 0-100. 
    // <20: Safe (Green)
    // 20-60: Suspicious (Amber)
    // >60: Danger (Red)

    let colorClass = styles.safe;
    let text = "SAFE";

    if (score > 60) {
        colorClass = styles.danger;
        text = "CRITICAL THREAT";
    } else if (score > 20) {
        colorClass = styles.warning;
        text = "SUSPICIOUS";
    }

    return (
        <div className={styles.container}>
            <div className={styles.statusText}>{text}</div>
            <div className={styles.scoreDisplay}>
                {score}%
            </div>
            <div className={styles.meterContainer}>
                <div
                    className={`${styles.meterFill} ${colorClass}`}
                    style={{ width: `${score}%` }}
                />
                {/* Tiks */}
                <div className={styles.tick} style={{ left: '25%' }} />
                <div className={styles.tick} style={{ left: '50%' }} />
                <div className={styles.tick} style={{ left: '75%' }} />
            </div>
            <p className={styles.label}>Threat Probability</p>
        </div>
    );
}
