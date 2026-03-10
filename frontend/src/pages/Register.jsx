import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Shield, Mail, Key, UserCheck } from 'lucide-react';
import styles from './Auth.module.css';

export function Register() {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);

    const handleRegister = (e) => {
        e.preventDefault();
        setLoading(true);
        setTimeout(() => {
            setLoading(false);
            navigate('/login');
        }, 1500);
    };

    return (
        <div className={styles.container}>
            <div className={styles.card}>
                <div className={styles.header}>
                    <h2 className={styles.title}>NEW OPERATOR</h2>
                    <p className={styles.subtitle}>Initialize new implementation sequence.</p>
                </div>

                <form onSubmit={handleRegister} className={styles.form}>
                    <div className={styles.inputGroup}>
                        <label className={styles.label}>Username</label>
                        <div className={styles.inputWrapper}>
                            <UserCheck className={styles.inputIcon} size={16} />
                            <input
                                type="text"
                                className={`${styles.input} ${styles.inputAmber}`}
                            />
                        </div>
                    </div>

                    <div className={styles.inputGroup}>
                        <label className={styles.label}>Email Frequency</label>
                        <div className={styles.inputWrapper}>
                            <Mail className={styles.inputIcon} size={16} />
                            <input
                                type="email"
                                className={`${styles.input} ${styles.inputAmber}`}
                            />
                        </div>
                    </div>

                    <div className={styles.inputGroup}>
                        <label className={styles.label}>Secure Key</label>
                        <div className={styles.inputWrapper}>
                            <Key className={styles.inputIcon} size={16} />
                            <input
                                type="password"
                                className={`${styles.input} ${styles.inputAmber}`}
                            />
                        </div>
                    </div>

                    <button
                        disabled={loading}
                        className={`${styles.submitBtn} ${styles.submitBtnAmber}`}
                    >
                        {loading ? "INITIALIZING..." : "JOIN NETWORK"}
                    </button>
                </form>

                <div className={`${styles.footerLink} ${styles.linkAmber}`}>
                    <Link to="/login">
                        Already authenticated? Return to Login
                    </Link>
                </div>
            </div>
        </div>
    );
}
