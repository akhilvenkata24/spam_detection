import { Link, useNavigate } from 'react-router-dom';
import styles from './Auth.module.css';

export function ForgotPassword() {
    const navigate = useNavigate();

    return (
        <div className={styles.container}>
            <div className={styles.card}>
                <div className={styles.header}>
                    <h2 className={styles.title}>COMING SOON</h2>
                    <p className={styles.subtitle}>Forgot password recovery is not available yet. We will add a secure reset flow later.</p>
                </div>

                <div className={styles.form} style={{ gap: '1rem' }}>
                    <div style={{ color: 'var(--muted-foreground)', fontSize: '0.9rem', lineHeight: 1.6 }}>
                        We are not shipping OTP-based recovery right now. Use your current login, or return later when the reset flow is ready.
                    </div>

                    <button className={styles.submitBtn} onClick={() => navigate('/login')}>
                        RETURN TO LOGIN
                    </button>
                </div>

                <div className={styles.footerLink}>
                    <Link to="/login">Return to Login</Link>
                </div>
            </div>
        </div>
    );
}
