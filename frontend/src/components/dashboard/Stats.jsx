import { useState, useEffect } from 'react';
import { LayoutDashboard, ShieldAlert, BadgeCheck } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import styles from './Dashboard.module.css';

export function Stats() {
    const { token } = useAuth();
    const [stats, setStats] = useState({ total_scans: 0, threats_blocked: 0, api_calls: 0 });

    useEffect(() => {
        if (!token) return;
        let isMounted = true;
        
        const fetchStats = async () => {
            try {
                const res = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000'}/api/dashboard/stats?_t=${Date.now()}`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                const data = await res.json();
                if (data.status === 'success' && isMounted) {
                    setStats(data.stats);
                }
            } catch (err) {
                console.error(err);
            }
        };

        fetchStats();
        const interval = setInterval(fetchStats, 3000);
        return () => {
            isMounted = false;
            clearInterval(interval);
        };
    }, [token]);

    return (
        <div className={styles.statsGrid}>
            <StatsCard
                title="Total Scans"
                value={stats.total_scans}
                icon={<LayoutDashboard size={16} className={styles.iconPrimary} />}
                trend="All time total combined"
            />
            <StatsCard
                title="Threats Blocked"
                value={stats.threats_blocked}
                icon={<ShieldAlert size={16} className={styles.iconBeforeDestructive} />}
                trend="Identified High Risk"
                trendClass={styles.textDestructive}
            />
            <StatsCard
                title="Safe Content Verified"
                value={stats.total_scans - stats.threats_blocked}
                icon={<BadgeCheck size={16} className={styles.textSuccess} />}
                trend="Secure validations"
                trendClass={styles.textSuccess}
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
