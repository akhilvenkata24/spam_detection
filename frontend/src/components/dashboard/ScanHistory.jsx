import { useState, useEffect } from 'react';
import { BadgeCheck, Smartphone, Globe, Trash2 } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import styles from './Dashboard.module.css';

export function ScanHistory() {
    const { token } = useAuth();
    const [scans, setScans] = useState([]);
    const [selectedIds, setSelectedIds] = useState(new Set());
    const [searchQuery, setSearchQuery] = useState("");

    useEffect(() => {
        if (!token) return;
        let isMounted = true;

        const pollHistory = async () => {
            try {
                const res = await fetch(`${import.meta.env.VITE_API_BASE_URL || \'http://127.0.0.1:5000\'}/api/dashboard/history?_t=${Date.now()}`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                const data = await res.json();
                if (data.status === 'success' && isMounted) {
                    setScans(data.history);
                }
            } catch (err) {
                console.error("Failed history pull", err);
            }
        };

        pollHistory();
        const interval = setInterval(pollHistory, 3000);
        
        return () => {
            isMounted = false;
            clearInterval(interval);
        };
    }, [token]);

    const handleDelete = async (e, id) => {
        e.stopPropagation();
        if (!confirm("Delete this scan record?")) return;
        try {
            const res = await fetch(`${import.meta.env.VITE_API_BASE_URL || \'http://127.0.0.1:5000\'}/api/dashboard/history/${id}`, {
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
            const res = await fetch(`${import.meta.env.VITE_API_BASE_URL || \'http://127.0.0.1:5000\'}/api/dashboard/history/bulk`, {
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
                            width: '250px'
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
                            <tr key={scan._id} className={styles.tr}>
                                <td className={styles.td}>
                                    <input 
                                        type="checkbox" 
                                        checked={selectedIds.has(scan._id)}
                                        onChange={(e) => handleSelect(e, scan._id)} 
                                    />
                                </td>
                                <td className={`${styles.td} ${styles.snippet}`}>{scan.text_snippet}</td>
                                <td className={styles.td}>
                                    <span className={`${styles.badge} ${scan.risk_score > 60 ? styles.badgeDanger :
                                        scan.risk_score > 20 ? styles.badgeWarn :
                                            styles.badgeSafe
                                        }`}>
                                        {scan.risk_score}%
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
                                <td className={`${styles.td} ${styles.date}`}>{new Date(scan.timestamp).toLocaleString()}</td>
                                <td className={styles.td}>
                                    <button 
                                        onClick={(e) => handleDelete(e, scan._id)} 
                                        style={{ background: 'none', border: 'none', color: 'var(--destructive)', cursor: 'pointer' }}
                                        title="Delete Record"
                                    >
                                        <Trash2 size={16} />
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    )
}
