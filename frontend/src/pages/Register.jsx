import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Shield, Mail, Key, UserCheck } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import styles from './Auth.module.css';

export function Register() {
    const navigate = useNavigate();
    const { register } = useAuth();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const handleRegister = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        
        const result = await register(username.trim(), email.trim(), password);
        if (result.success) {
            navigate('/login');
        } else {
            setError(result.message);
            setLoading(false);
        }
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
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                required
                            />
                        </div>
                    </div>

                    <div className={styles.inputGroup}>
                        <label className={styles.label}>Email Address</label>
                        <div className={styles.inputWrapper}>
                            <Mail className={styles.inputIcon} size={16} />
                            <input
                                type="email"
                                className={`${styles.input} ${styles.inputAmber}`}
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
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
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                        </div>
                    </div>
                    
                    {error && <div style={{color: 'red', marginTop: '10px', fontSize: '0.9rem'}}>{error}</div>}

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
