import { Stats } from '../components/dashboard/Stats';
import { ScanHistory } from '../components/dashboard/ScanHistory';
import { SystemHealth } from '../components/dashboard/SystemHealth';
import { Settings } from '../components/dashboard/Settings';
import { SmsManager } from '../components/dashboard/SmsManager';
import { ShieldAlert } from 'lucide-react';
import styles from '../components/dashboard/Dashboard.module.css';

export function Dashboard() {
    return (
        <div className={styles.dashboardFn}>
            <div className={styles.cyberGrid} />
            <h1 className={styles.pageTitle}>Command Center</h1>

            <Stats />

            <div className={styles.mainGrid}>
                <div className={styles.historySection}>
                    <ScanHistory />
                    <SmsManager />
                </div>
                <div className={styles.sidebar}>
                    <Settings />
                    <div className={styles.qrWidget}>
                        <h3 className={styles.sectionTitle} style={{ marginBottom: '0.5rem' }}>Mobile Sync App</h3>
                        <p className={styles.sectionDesc} style={{ marginBottom: '0.85rem' }}>
                            Scan to install the companion mobile app and sync messages.
                        </p>
                        <div className={styles.qrWidgetFrame}>
                            <img src="/SPAM_DETECT_V2.svg" alt="Mobile app QR placeholder" className={styles.qrWidgetImage} />
                        </div>
                        <div className={styles.qrWidgetCaution}>
                            <ShieldAlert size={14} />
                            <span>
                                Pause Play Protect during install, then turn it back on. Sensitive-info checks can block setup.
                            </span>
                        </div>
                    </div>
                    <SystemHealth />
                </div>
            </div>
        </div>
    );
}
