import { BadgeCheck, Smartphone, Globe } from 'lucide-react';
import styles from './Dashboard.module.css';

export function ScanHistory() {
    const scans = [
        { id: 1, text: "URGENT! Your account is locked...", score: 95, source: "API (Mobile)", date: "2 mins ago" },
        { id: 3, text: "Win a free iPhone 15 Pro Max!", score: 88, source: "API (Mobile)", date: "1 hour ago" },
        { id: 4, text: "Verify your bank details immediately", score: 92, source: "Web", date: "3 hours ago" },
    ].filter(s => s.score > 60);

    return (
        <div className={styles.historyCard}>
            <div className={styles.historyHeader}>
                <h3 className={styles.historyTitle}>Recent Scan History</h3>
            </div>
            <div className={styles.tableContainer}>
                <table className={styles.table}>
                    <thead className={styles.thead}>
                        <tr>
                            <th className={styles.th}>Message Snippet</th>
                            <th className={styles.th}>Risk Score</th>
                            <th className={styles.th}>Source</th>
                            <th className={styles.th}>Time</th>
                        </tr>
                    </thead>
                    <tbody>
                        {scans.map((scan) => (
                            <tr key={scan.id} className={styles.tr}>
                                <td className={`${styles.td} ${styles.snippet}`}>{scan.text}</td>
                                <td className={styles.td}>
                                    <span className={`${styles.badge} ${scan.score > 60 ? styles.badgeDanger :
                                        scan.score > 20 ? styles.badgeWarn :
                                            styles.badgeSafe
                                        }`}>
                                        {scan.score}%
                                    </span>
                                </td>
                                <td className={styles.td}>
                                    <span className={styles.sourceBadge}>
                                        {scan.source.includes("API") ? (
                                            <>
                                                <Smartphone size={16} className={styles.textAmber} />
                                                <span className={`${styles.pill} ${styles.pillMobile}`}>MOBILE</span>
                                            </>
                                        ) : (
                                            <>
                                                <Globe size={16} className={styles.textPrimary} />
                                                <span className={`${styles.pill} ${styles.pillWeb}`}>WEB</span>
                                            </>
                                        )}
                                    </span>
                                </td>
                                <td className={`${styles.td} ${styles.date}`}>{scan.date}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    )
}
