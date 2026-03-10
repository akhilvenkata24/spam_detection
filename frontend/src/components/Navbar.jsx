import { Link, useLocation } from 'react-router-dom';
import { ShieldCheck, LayoutDashboard } from 'lucide-react';
import styles from './Navbar.module.css';

export function Navbar() {
    const location = useLocation();
    const isActive = (path) => location.pathname === path;

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
                    <Link to="/login">
                        <button className={styles.loginBtn}>Login</button>
                    </Link>
                    <Link to="/register">
                        <button className={styles.registerBtn}>Register</button>
                    </Link>
                </div>
            </div>
        </nav>
    );
}
