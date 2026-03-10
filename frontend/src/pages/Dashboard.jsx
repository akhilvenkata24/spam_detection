import { Stats } from '../components/dashboard/Stats';
import { ScanHistory } from '../components/dashboard/ScanHistory';
import { ApiManager } from '../components/dashboard/ApiManager';
import { Settings } from '../components/dashboard/Settings';
import styles from '../components/dashboard/Dashboard.module.css';

export function Dashboard() {
    return (
        <div className={styles.dashboardFn}>
            <h1 className={styles.pageTitle}>Command Center</h1>

            <Stats />

            <div className={styles.mainGrid}>
                <div className={styles.historySection}>
                    <ScanHistory />
                </div>
                <div className={styles.sidebar}>
                    <Settings />
                </div>
            </div>
        </div>
    );
}
