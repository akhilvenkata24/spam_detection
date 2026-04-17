import { Stats } from '../components/dashboard/Stats';
import { ScanHistory } from '../components/dashboard/ScanHistory';
import { SystemHealth } from '../components/dashboard/SystemHealth';
import { Settings } from '../components/dashboard/Settings';
import { SmsManager } from '../components/dashboard/SmsManager';
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
                    <SystemHealth />
                </div>
            </div>
        </div>
    );
}
