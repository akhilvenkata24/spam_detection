import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Lock, User, Terminal } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import styles from './Auth.module.css';

export function Login() {
    const navigate = useNavigate();
    const { login } = useAuth();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    const handleLogin = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        
        const result = await login(username, password);
        if (!result.success) {
            setError(result.message);
            setLoading(false);
        }
    };

    return (
        <div className={styles.container}>
            <div className={styles.card}>
                <div className={styles.laser} />
                <div className={styles.topGlow} />

                <div className={styles.header}>
                    <h2 className={styles.title}>ACCESS TERMINAL</h2>
                    <p className={styles.subtitle}>Enter credentials to access the forensics system.</p>
                </div>

                <form onSubmit={handleLogin} className={styles.form}>
                    <div className={styles.inputGroup}>
                        <label className={styles.label}>User ID</label>
                        <div className={styles.inputWrapper}>
                            <User className={styles.inputIcon} size={20} />
                            <input
                                type="text"
                                className={styles.input}
                                placeholder="sys_admin"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                required
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
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                        </div>
                    </div>

                    {error && <div style={{color: 'red', marginTop: '10px', fontSize: '0.9rem'}}>{error}</div>}

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
