import { useState, useEffect } from 'react';
import { Smartphone, Globe, Trash2, RefreshCw } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { apiUrl } from '../../lib/api';
import { getRetentionCountdownLabel } from '../../lib/retention';
import styles from './Dashboard.module.css';

const VERDICT_META = {
    safe: { label: 'Verified Safe', className: 'badgeSafe' },
    suspicious: { label: 'Suspicious', className: 'badgeWarn' },
    high_risk: { label: 'High Risk', className: 'badgeDanger' },
    fraud: { label: 'Severe Threat', className: 'badgeDanger' }
};

const MOBILE_SOURCES = new Set(['API (Mobile)', 'Mobile Manual Scan', 'Mobile SMS Sync']);

const getVerdictMeta = (verdict) => {
    const normalizedVerdict = String(verdict || '').toLowerCase();
    return VERDICT_META[normalizedVerdict] || VERDICT_META.suspicious;
};

const getSourceMeta = (source) => {
    const normalizedSource = String(source || '').trim();
    if (normalizedSource === 'Web') {
        return {
            isMobile: false,
            label: 'WEB'
        };
    }

    if (MOBILE_SOURCES.has(normalizedSource)) {
        return {
            isMobile: true,
            label: 'MOBILE'
        };
    }

    return {
        isMobile: false,
        label: 'WEB'
    };
};

export function ScanHistory() {
    const { token } = useAuth();
    const [scans, setScans] = useState([]);
    const [selectedIds, setSelectedIds] = useState(new Set());
    const [searchQuery, setSearchQuery] = useState("");
    const [selectedScan, setSelectedScan] = useState(null);
    const [clockTick, setClockTick] = useState(Date.now());
    const [isRefreshing, setIsRefreshing] = useState(false);

    const fetchHistory = async () => {
        if (!token) return;
        try {
            const res = await fetch(`${apiUrl('/api/dashboard/history')}?_t=${Date.now()}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await res.json();
            if (data.status === 'success') {
                setScans(data.history);
            }
        } catch (err) {
            console.error("Failed history pull", err);
        }
    };

    const handleScanClick = (scan) => {
        setSelectedScan(scan);
    };

    const closeModal = () => {
        setSelectedScan(null);
    };

    useEffect(() => {
        if (!token) return;
        let isMounted = true;

        const pollHistory = async () => {
            if (!isMounted) return;
            await fetchHistory();
        };

        pollHistory();
        const interval = setInterval(pollHistory, 3000);
        
        return () => {
            isMounted = false;
            clearInterval(interval);
        };
    }, [token]);

    useEffect(() => {
        const timer = setInterval(() => setClockTick(Date.now()), 60000);
        return () => clearInterval(timer);
    }, []);

    const handleDelete = async (e, id) => {
        e.stopPropagation();
        if (!confirm("Delete this scan record?")) return;
        try {
            const res = await fetch(apiUrl(`/api/dashboard/history/${id}`), {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                setScans(scans.filter(s => s._id !== id));
                const newSelected = new Set(selectedIds);
                newSelected.delete(id);
                setSelectedIds(newSelected);
            }
        } catch (err) {
            console.error(err);
        }
    };

    const handleSelectAll = (e) => {
        if (e.target.checked) {
            setSelectedIds(new Set(filteredScans.map(s => s._id)));
        } else {
            setSelectedIds(new Set());
        }
    };

    const handleSelect = (e, id) => {
        const newSelected = new Set(selectedIds);
        if (e.target.checked) {
            newSelected.add(id);
        } else {
            newSelected.delete(id);
        }
        setSelectedIds(newSelected);
    };

    const handleBulkDelete = async () => {
        if (selectedIds.size === 0) return;
        if (!confirm(`Delete ${selectedIds.size} records?`)) return;
        try {
            const res = await fetch(apiUrl('/api/dashboard/history/bulk'), {
                method: 'DELETE',
                headers: { 
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json' 
                },
                body: JSON.stringify({ ids: Array.from(selectedIds) })
            });
            if (res.ok) {
                setScans(scans.filter(s => !selectedIds.has(s._id)));
                setSelectedIds(new Set());
            }
        } catch (err) {
            console.error(err);
        }
    };

    const handleRefresh = async () => {
        setIsRefreshing(true);
        try {
            await fetchHistory();
        } finally {
            setIsRefreshing(false);
        }
    };

    const filteredScans = scans.filter(s => {
        if (!searchQuery) return true;
        const q = searchQuery.toLowerCase();
        const dateStr = new Date(s.timestamp).toLocaleString().toLowerCase();
        return (
            (s.text_snippet && s.text_snippet.toLowerCase().includes(q)) ||
            (s.source && s.source.toLowerCase().includes(q)) ||
            dateStr.includes(q)
        );
    });

    return (
        <div className={styles.historyCard}>
            <div className={styles.historyHeader} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <h3 className={styles.historyTitle} style={{ margin: 0 }}>Recent Scan History ({filteredScans.length}/{scans.length})</h3>
                    <input 
                        type="text" 
                        placeholder="Search snippets, source, date..." 
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        style={{
                            padding: '0.4rem 1rem',
                            borderRadius: '4px',
                            border: '1px solid var(--border)',
                            background: 'rgba(0,0,0,0.5)',
                            color: 'var(--foreground)',
                            width: 'min(250px, 100%)'
                        }}
                    />
                </div>
                {selectedIds.size > 0 && (
                    <button 
                        onClick={handleBulkDelete}
                        style={{ background: 'var(--destructive)', color: '#fff', padding: '0.25rem 0.75rem', borderRadius: '4px', fontSize: '0.875rem' }}
                    >
                        Delete Selected ({selectedIds.size})
                    </button>
                )}
                <button
                    onClick={handleRefresh}
                    disabled={isRefreshing}
                    style={{ background: 'var(--primary)', color: '#fff', padding: '0.25rem 0.75rem', borderRadius: '4px', fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.4rem', opacity: isRefreshing ? 0.7 : 1 }}
                    title="Refresh scan history"
                >
                    <RefreshCw size={14} />
                    {isRefreshing ? 'Refreshing' : 'Refresh'}
                </button>
            </div>
            <div className={styles.tableContainer} style={{ maxHeight: '400px', overflowY: 'auto' }}>
                <table className={styles.table}>
                    <thead className={styles.thead} style={{ position: 'sticky', top: 0 }}>
                        <tr>
                            <th className={styles.th} style={{ width: '40px' }}>
                                <input 
                                    type="checkbox" 
                                    checked={selectedIds.size === filteredScans.length && filteredScans.length > 0}
                                    onChange={handleSelectAll} 
                                />
                            </th>
                            <th className={styles.th}>Message Snippet</th>
                            <th className={styles.th}>Risk Score</th>
                            <th className={styles.th}>Source</th>
                            <th className={styles.th}>Time</th>
                            <th className={styles.th}></th>
                        </tr>
                    </thead>
                    <tbody>
                        {scans.length === 0 && (
                            <tr><td colSpan="6" style={{textAlign: "center", padding: "20px", color: "var(--muted)"}}>No scan history found.</td></tr>
                        )}
                        {filteredScans.map((scan) => (
                            (() => {
                                const verdictMeta = getVerdictMeta(scan.verdict);
                                const sourceMeta = getSourceMeta(scan.source);

                                return (
                            <tr 
                                key={scan._id} 
                                className={styles.tr}
                                onClick={() => handleScanClick(scan)}
                                style={{ cursor: 'pointer' }}
                                title="Click to view full analysis"
                            >
                                <td className={styles.td} data-label="Select" onClick={e => e.stopPropagation()}>
                                    <input 
                                        type="checkbox" 
                                        checked={selectedIds.has(scan._id)}
                                        onChange={(e) => handleSelect(e, scan._id)} 
                                    />
                                </td>
                                <td className={`${styles.td} ${styles.snippet}`} data-label="Message Snippet">{scan.text_snippet}</td>
                                <td className={styles.td} data-label="Risk Score">
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', alignItems: 'flex-start' }}>
                                        <span className={`${styles.badge} ${scan.risk_score > 60 ? styles.badgeDanger :
                                            scan.risk_score > 20 ? styles.badgeWarn :
                                                styles.badgeSafe
                                            }`}>
                                            {scan.risk_score}%
                                        </span>
                                        <span className={`${styles.badge} ${styles[verdictMeta.className]}`}>
                                            {verdictMeta.label}
                                        </span>
                                    </div>
                                </td>
                                <td className={styles.td} data-label="Source">
                                    <span className={styles.sourceBadge}>
                                        {sourceMeta.isMobile ? (
                                            <>
                                                <Smartphone size={16} className={styles.textAmber} />
                                                <span className={`${styles.pill} ${styles.pillMobile}`}>MOBILE</span>
                                            </>
                                        ) : (
                                            <>
                                                <Globe size={16} className={styles.textPrimary} />
                                                <span className={`${styles.pill} ${styles.pillWeb}`}>{sourceMeta.label}</span>
                                            </>
                                        )}
                                    </span>
                                </td>
                                <td className={`${styles.td} ${styles.date}`} data-label="Time">
                                    <div>{new Date(scan.timestamp).toLocaleString()}</div>
                                    <div className={styles.retentionNote}>{getRetentionCountdownLabel(scan, clockTick)}</div>
                                </td>
                                <td className={styles.td} data-label="Actions">
                                    <button 
                                        onClick={(e) => handleDelete(e, scan._id)} 
                                        style={{ background: 'none', border: 'none', color: 'var(--destructive)', cursor: 'pointer' }}
                                        title="Delete Record"
                                    >
                                        <Trash2 size={16} />
                                    </button>
                                </td>
                            </tr>
                                );
                            })()
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Analysis Modal */}
            {selectedScan && (
                (() => {
                    const verdictMeta = getVerdictMeta(selectedScan.verdict);

                    return (
                <div style={{
                    position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', 
                    background: 'rgba(0,0,0,0.8)', display: 'flex', justifyContent: 'center', 
                    alignItems: 'center', zIndex: 1000
                }} onClick={closeModal}>
                    <div 
                        style={{
                            background: 'var(--background)', border: '1px solid var(--border)',
                            borderRadius: '8px', padding: '2rem', maxWidth: '500px', width: '90%',
                            boxShadow: '0 10px 25px rgba(0,0,0,0.5)'
                        }}
                        onClick={e => e.stopPropagation()}
                    >
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
                            <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>Scan Details</h2>
                            <button onClick={closeModal} style={{ background: 'none', border: 'none', color: 'var(--muted-foreground)', cursor: 'pointer', fontSize: '1.25rem' }}>&times;</button>
                        </div>
                        
                        {selectedScan.sender && (
                            <div style={{ marginBottom: '1.5rem' }}>
                                <h4 style={{ color: 'var(--muted-foreground)', fontSize: '0.875rem', marginBottom: '0.5rem' }}>Sender</h4>
                                <p style={{ fontWeight: 'bold', fontSize: '1.1rem' }}>{selectedScan.sender}</p>
                            </div>
                        )}

                        <div style={{ marginBottom: '1.5rem', background: 'rgba(26,26,26,0.5)', padding: '1rem', borderRadius: '4px' }}>
                            <h4 style={{ color: 'var(--muted-foreground)', fontSize: '0.875rem', marginBottom: '0.5rem' }}>Full Message</h4>
                            <p style={{ lineHeight: '1.5', whiteSpace: 'pre-wrap' }}>
                                {selectedScan.full_text || selectedScan.text_snippet}
                            </p>
                        </div>

                        <div style={{ display: 'flex', gap: '2rem', marginBottom: '1.5rem' }}>
                            <div>
                                <h4 style={{ color: 'var(--muted-foreground)', fontSize: '0.875rem', marginBottom: '0.5rem' }}>Threat Verdict</h4>
                                <span className={`${styles.badge} ${styles[verdictMeta.className]}`} style={{ fontSize: '1rem', padding: '0.5rem 1rem' }}>
                                    {verdictMeta.label}
                                </span>
                            </div>
                            <div>
                                <h4 style={{ color: 'var(--muted-foreground)', fontSize: '0.875rem', marginBottom: '0.5rem' }}>Risk Score</h4>
                                <span style={{ fontSize: '1.25rem', fontWeight: 'bold', color: selectedScan.risk_score > 60 ? 'var(--destructive)' : selectedScan.risk_score > 20 ? 'var(--cyber-amber)' : 'var(--primary)' }}>
                                    {selectedScan.risk_score}%
                                </span>
                            </div>
                        </div>

                        <div className={styles.retentionNote} style={{ marginBottom: '1rem' }}>
                            {getRetentionCountdownLabel(selectedScan, clockTick)}
                        </div>

                        <div style={{ fontSize: '0.875rem', color: 'var(--muted-foreground)' }}>
                            Processed on: {new Date(selectedScan.timestamp).toLocaleString()}
                        </div>
                    </div>
                </div>
                    );
                })()
            )}
        </div>
    )
}
