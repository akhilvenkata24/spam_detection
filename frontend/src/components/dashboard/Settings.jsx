import { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { apiUrl } from '../../lib/api';
import styles from './Dashboard.module.css';

export function Settings() {
    const { user, token, updateAuthUser } = useAuth();
    const [threshold, setThreshold] = useState(60);
    const [autoFlag, setAutoFlag] = useState(false);
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        if (user && user.settings) {
            setThreshold(user.settings.storage_threshold);
            setAutoFlag(user.settings.auto_flag);
        }
    }, [user]);

    const handleSave = async () => {
        setSaving(true);
        const newSettings = { storage_threshold: parseInt(threshold), auto_flag: autoFlag };
        
        try {
                const res = await fetch(apiUrl('/api/dashboard/settings'), {
                method: 'PUT',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}` 
                },
                body: JSON.stringify({ settings: newSettings })
            });
            if (res.ok) {
                updateAuthUser({ settings: newSettings });
            }
        } catch (err) {
            console.error("Failed to save settings");
        }
        setTimeout(() => setSaving(false), 500);
    };

    return (
        <div className={styles.settingsCard}>
            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                <h3 className={styles.sectionTitle}>Analysis Configuration</h3>
                <button 
                    onClick={handleSave} 
                    style={{background: 'var(--amber)', color: 'black', border: 'none', padding: '5px 10px', cursor: 'pointer', borderRadius: '4px', fontWeight: 'bold'}}
                >
                    {saving ? 'Saved!' : 'Save'}
                </button>
            </div>

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
                        Only save messages to the database if the risk score is at or above <span style={{ fontWeight: 'bold', color: 'var(--foreground)' }}>{threshold}%</span>.
                        Low-risk messages will be discarded after analysis to save space.
                    </p>
                </div>

                <div className={styles.toggleRow}>
                    <span className={styles.sliderLabel}>Auto-Flag Malicious Links</span>
                    <label className={styles.toggleSwitch}>
                        <input 
                            type="checkbox" 
                            className={styles.toggleInput} 
                            checked={autoFlag}
                            onChange={(e) => setAutoFlag(e.target.checked)}
                        />
                        <span className={styles.toggleSlider}></span>
                    </label>
                </div>
            </div>

        </div>
    )
}
