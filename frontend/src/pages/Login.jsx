import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Lock, User, Terminal } from 'lucide-react';
import styles from './Auth.module.css';

export function Login() {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);

    const handleLogin = (e) => {
        e.preventDefault();
        setLoading(true);
        setTimeout(() => {
            setLoading(false);
            navigate('/dashboard');
        }, 1500);
    };

    return (
        <div className={styles.container}>
            <div className={styles.card}>
                <div className={styles.topGlow} />

                <div className={styles.header}>
                    <h2 className={styles.title}>ACCESS TERMINAL</h2>
                    <p className={styles.subtitle}>Enter credentials to access the forensics system.</p>
                </div>

                <form onSubmit={handleLogin} className={styles.form}>
                    <div className={styles.inputGroup}>
                        <label className={styles.label}>Operator ID</label>
                        <div className={styles.inputWrapper}>
                            <User className={styles.inputIcon} size={20} />
                            <input
                                type="text"
                                className={styles.input}
                                placeholder="admin_sys"
                                defaultValue="admin_sys"
                            />
                        </div>
                    </div>

                    <div className={styles.inputGroup}>
                        <label className={styles.label}>Passphrase</label>
                        <div className={styles.inputWrapper}>
                            <Lock className={styles.inputIcon} size={20} />
                            <input
                                type="password"
                                className={styles.input}
                                placeholder="••••••••"
                                defaultValue="password"
                            />
                        </div>
                    </div>

                    <button disabled={loading} className={styles.submitBtn}>
                        {loading ? (
                            <span className={styles.pulse}>AUTHENTICATING...</span>
                        ) : (
                            <>UNLOCK SYSTEM <span className={styles.arrow}>→</span></>
                        )}
                    </button>
                </form>

                <div className={styles.footerLink}>
                    <Link to="/register">
                        Request Access Level (Register)
                    </Link>
                </div>
            </div>
        </div>
    );
}
