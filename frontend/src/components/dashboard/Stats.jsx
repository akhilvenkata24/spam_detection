import { LayoutDashboard, ShieldAlert, Key } from 'lucide-react';
import styles from './Dashboard.module.css';

export function Stats() {
    return (
        <div className={styles.statsGrid}>
            <StatsCard
                title="Total Scans"
                value="1,284"
                icon={<LayoutDashboard size={16} className={styles.iconPrimary} />}
                trend="+12% from last week"
            />
            <StatsCard
                title="Threats Blocked"
                value="342"
                icon={<ShieldAlert size={16} className={styles.iconBeforeDestructive} />}
                trend="+5% from last week"
                trendClass={styles.textDestructive}
            />
            <StatsCard
                title="API Calls"
                value="892"
                icon={<Key size={16} className={styles.textAmber} />}
                trend="Mobile App Source"
            />
        </div>
    )
}

function StatsCard({ title, value, icon, trend, trendClass = styles.textSuccess }) {
    return (
        <div className={styles.statsCard}>
            <div className={styles.cardHeader}>
                <h3 className={styles.cardTitle}>{title}</h3>
                {icon}
            </div>
            <div className={styles.cardValue}>{value}</div>
            <p className={`${styles.cardTrend} ${trendClass}`}>{trend}</p>
        </div>
    )
}
