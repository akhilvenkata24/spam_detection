import { AlertTriangle, CheckCircle, XCircle } from 'lucide-react';
import { RiskMeter } from './RiskMeter';
import styles from './AnalysisResult.module.css';

export function AnalysisResult({ result, onReset }) {
    if (!result) return null;

    const { score, flags, details } = result;

    return (
        <div className={styles.container}>
            <div className={styles.grid}>
                <div className={styles.riskCard}>
                    <RiskMeter score={score} />
                </div>

                <div className={styles.detailsColumn}>
                    <div className={styles.infoCard}>
                        <h3 className={styles.cardTitle}>
                            <AlertTriangle className={styles.warningIcon} size={20} />
                            ANALYSIS DETAILS
                        </h3>
                        <ul className={styles.list}>
                            {details.map((item, idx) => (
                                <li key={idx} className={styles.listItem}>
                                    <span className={styles.label}>{item.label}</span>
                                    <span className={`${styles.value} ${item.risk ? styles.textDanger : styles.textSafe}`}>
                                        {item.value}
                                    </span>
                                </li>
                            ))}
                        </ul>
                    </div>

                    <div className={styles.infoCard}>
                        <h3 className={styles.cardTitle}>DETECTED FLAGS</h3>
                        <div className={styles.flagsWrapper}>
                            {flags.length === 0 ? (
                                <span className={styles.noFlags}><CheckCircle size={16} /> No specific flags detected.</span>
                            ) : (
                                flags.map((flag, idx) => (
                                    <span key={idx} className={styles.flag}>
                                        <XCircle size={12} /> {flag}
                                    </span>
                                ))
                            )}
                        </div>
                    </div>
                </div>
            </div>

            <div className={styles.actions}>
                <button onClick={onReset} className={styles.resetBtn}>
                    Start New Scan
                </button>
            </div>
        </div>
    );
}
