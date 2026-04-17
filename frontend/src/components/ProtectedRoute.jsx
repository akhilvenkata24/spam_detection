import { Link, useLocation } from 'react-router-dom';
import { AlertTriangle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import styles from './ProtectedRoute.module.css';

export function ProtectedRoute({ children }) {
    const { token, loading } = useAuth();
    const location = useLocation();
    const persistedToken = localStorage.getItem('token');
    const sessionToken = sessionStorage.getItem('token');
    const effectiveToken = token || persistedToken || sessionToken;
    const loginSuccessState = Boolean(location.state?.authSuccess);
    const queryAuth = new URLSearchParams(location.search).get('auth') === '1';

    if (loading) {
        return null;
    }

    if (!effectiveToken && !loginSuccessState && !queryAuth) {
        return (
            <div className={styles.overlay}>
                <div className={styles.popup}>
                    <div className={styles.iconWrap}>
                        <AlertTriangle size={26} className={styles.icon} />
                    </div>
                    <h2 className={styles.title}>Access Restricted</h2>
                    <p className={styles.message}>
                        Please log in first to open the dashboard.
                    </p>
                    <Link to="/login" className={styles.loginBtn}>
                        Go To Login
                    </Link>
                </div>
            </div>
        );
    }

    return children;
}
