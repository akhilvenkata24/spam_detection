import { Activity, Database, Shield, Cpu } from 'lucide-react';
import styles from './Dashboard.module.css';

export function SystemHealth() {
    return (
        <div className={styles.settingsCard} style={{ marginTop: '1rem', position: 'relative', overflow: 'hidden' }}>
            <div style={{ position: 'absolute', top: '-50px', right: '-50px', width: '150px', height: '150px', background: 'var(--primary)', filter: 'blur(80px)', opacity: 0.15, borderRadius: '50%', zIndex: 0 }} />
            
            <div style={{ position: 'relative', zIndex: 1 }}>
                <h3 className={styles.sectionTitle} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Activity size={18} className={styles.textPrimary} />
                    System Health
                </h3>
                <p className={styles.sectionDesc}>
                    Live telemetry across threat analysis nodes.
                </p>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1.5rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(0,0,0,0.3)', padding: '0.75rem', borderRadius: '6px', borderLeft: '3px solid var(--success)' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                            <Cpu size={18} style={{ color: 'var(--success)' }} />
                            <div>
                                <h4 style={{ fontSize: '0.875rem', margin: 0, fontWeight: 'bold' }}>ML Analysis Engine</h4>
                                <span style={{ fontSize: '0.75rem', color: 'var(--muted-foreground)' }}>v2.4.1 (Aggressive)</span>
                            </div>
                        </div>
                        <span className={`${styles.badge} ${styles.badgeSafe}`}>ONLINE</span>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(0,0,0,0.3)', padding: '0.75rem', borderRadius: '6px', borderLeft: '3px solid var(--primary)' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                            <Shield size={18} style={{ color: 'var(--primary)' }} />
                            <div>
                                <h4 style={{ fontSize: '0.875rem', margin: 0, fontWeight: 'bold' }}>Heuristics Database</h4>
                                <span style={{ fontSize: '0.75rem', color: 'var(--muted-foreground)' }}>Updated 2 mins ago</span>
                            </div>
                        </div>
                        <span className={styles.textPrimary} style={{ fontSize: '0.875rem', fontWeight: 'bold' }}>SYNCED</span>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(0,0,0,0.3)', padding: '0.75rem', borderRadius: '6px', borderLeft: '3px solid var(--amber)' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                            <Database size={18} style={{ color: 'var(--amber)' }} />
                            <div>
                                <h4 style={{ fontSize: '0.875rem', margin: 0, fontWeight: 'bold' }}>Data Redundancy</h4>
                                <span style={{ fontSize: '0.75rem', color: 'var(--muted-foreground)' }}>MongoDB Cluster 0</span>
                            </div>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <span className={styles.pulseIndicator} style={{ width: '8px', height: '8px', background: 'var(--amber)', borderRadius: '50%', display: 'inline-block' }}></span>
                            <span style={{ fontSize: '0.875rem', color: 'var(--amber)', fontWeight: 'bold' }}>ACTIVE</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
