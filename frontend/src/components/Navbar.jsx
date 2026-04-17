import { Link, useLocation } from 'react-router-dom';
import { ShieldCheck, LayoutDashboard, LogOut } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import styles from './Navbar.module.css';

export function Navbar() {
    const { user, token, logout } = useAuth();
    const location = useLocation();
    const isActive = (path) => location.pathname === path;
    const displayName = user?.username || 'USER';
    const hasSession = Boolean(token || user);

    return (
        <nav className={styles.navbar}>
            <div className={styles.container}>
                <Link to="/" className={styles.brand}>
                    <ShieldCheck className={styles.logoIcon} />
                    <span className={styles.logoText}>
                        SPAM<span className={styles.textPrimary}>.DETECT</span>
                    </span>
                </Link>

                <div className={styles.navLinks}>
                    <Link to="/" className={`${styles.navLink} ${isActive('/') ? styles.active : ''}`}>
                        <ShieldCheck size={16} style={{ marginRight: '0.5rem' }} />
                        Scanner
                    </Link>
                    <Link to="/dashboard" className={`${styles.navLink} ${isActive('/dashboard') ? styles.active : ''}`}>
                        <LayoutDashboard size={16} style={{ marginRight: '0.5rem' }} />
                        Dashboard
                    </Link>
                </div>

                <div className={styles.authButtons}>
                    {hasSession ? (
                        <>
                            <span style={{ color: "var(--amber)", fontSize: "0.9rem", marginRight: "1rem" }}>
                                {displayName}
                            </span>
                            <button className={styles.loginBtn} onClick={logout} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                <LogOut size={14} /> Logout
                            </button>
                        </>
                    ) : (
                        <>
                            <Link to="/login">
                                <button className={styles.loginBtn}>Login</button>
                            </Link>
                            <Link to="/register">
                                <button className={styles.registerBtn}>Register</button>
                            </Link>
                        </>
                    )}
                </div>
            </div>
        </nav>
    );
}
