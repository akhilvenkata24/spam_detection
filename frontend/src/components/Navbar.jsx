import { useEffect, useRef, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ShieldCheck, LayoutDashboard, LogOut, ChevronDown, Mail, Lock, User, X } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import styles from './Navbar.module.css';

export function Navbar() {
    const { user, token, logout, updateProfile, changePassword } = useAuth();
    const location = useLocation();
    const menuRef = useRef(null);
    const [accountOpen, setAccountOpen] = useState(false);
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [profilePassword, setProfilePassword] = useState('');
    const [oldPassword, setOldPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmNewPassword, setConfirmNewPassword] = useState('');
    const [profileSaving, setProfileSaving] = useState(false);
    const [passwordSaving, setPasswordSaving] = useState(false);
    const [profileMessage, setProfileMessage] = useState('');
    const [passwordMessage, setPasswordMessage] = useState('');
    const [profileError, setProfileError] = useState('');
    const [passwordError, setPasswordError] = useState('');

    const isActive = (path) => location.pathname === path;
    const displayName = user?.username || 'USER';
    const hasSession = Boolean(token || user);

    useEffect(() => {
        setUsername(user?.username || '');
        setEmail(user?.email || '');
        setProfileMessage('');
        setPasswordMessage('');
        setProfileError('');
        setPasswordError('');
    }, [user]);

    useEffect(() => {
        const handleOutsideClick = (event) => {
            if (menuRef.current && !menuRef.current.contains(event.target)) {
                setAccountOpen(false);
            }
        };

        document.addEventListener('mousedown', handleOutsideClick);
        return () => document.removeEventListener('mousedown', handleOutsideClick);
    }, []);

    const handleProfileSave = async () => {
        setProfileError('');
        setProfileMessage('');
        setProfileSaving(true);
        if (!profilePassword) {
            setProfileError('Current password is required to update account details.');
            setProfileSaving(false);
            return;
        }

        const result = await updateProfile({
            username: username.trim(),
            email: email.trim(),
            current_password: profilePassword,
        });
        if (!result.success) {
            setProfileError(result.message);
        } else {
            setProfileMessage(result.message || 'Profile updated');
            setProfilePassword('');
        }
        setProfileSaving(false);
    };

    const handlePasswordSave = async () => {
        setPasswordError('');
        setPasswordMessage('');

        if (!oldPassword || !newPassword || !confirmNewPassword) {
            setPasswordError('Old password, new password, and confirm new password are required.');
            return;
        }

        if (newPassword !== confirmNewPassword) {
            setPasswordError('New password and confirmation do not match.');
            return;
        }

        setPasswordSaving(true);
        const result = await changePassword(oldPassword, newPassword);
        if (!result.success) {
            setPasswordError(result.message);
        } else {
            setPasswordMessage(result.message || 'Password updated');
            setOldPassword('');
            setNewPassword('');
            setConfirmNewPassword('');
        }
        setPasswordSaving(false);
    };

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

                <div className={styles.authButtons} ref={menuRef}>
                    {hasSession ? (
                        <>
                            <div className={styles.accountMenuWrap}>
                                <button
                                    type="button"
                                    className={styles.accountTrigger}
                                    onClick={() => setAccountOpen((value) => !value)}
                                    aria-expanded={accountOpen}
                                    aria-haspopup="dialog"
                                >
                                    <User size={14} />
                                    <span>{displayName}</span>
                                    <ChevronDown size={14} className={accountOpen ? styles.chevronOpen : ''} />
                                </button>

                                {accountOpen && (
                                    <div className={styles.accountMenu} role="dialog" aria-label="Account details">
                                        <div className={styles.accountMenuHeader}>
                                            <div>
                                                <div className={styles.accountMenuTitle}>Account Details</div>
                                                <div className={styles.accountMenuMeta}>{user?.email || 'No email on file'}</div>
                                            </div>
                                            <button type="button" className={styles.iconBtn} onClick={() => setAccountOpen(false)} aria-label="Close account panel">
                                                <X size={14} />
                                            </button>
                                        </div>

                                        <div className={styles.accountGroup}>
                                            <label className={styles.accountLabel}>Username</label>
                                            <div className={styles.accountInputRow}>
                                                <User size={14} />
                                                <input
                                                    type="text"
                                                    value={username}
                                                    onChange={(e) => setUsername(e.target.value)}
                                                    className={styles.accountInput}
                                                />
                                            </div>
                                        </div>

                                        <div className={styles.accountGroup}>
                                            <label className={styles.accountLabel}>Email</label>
                                            <div className={styles.accountInputRow}>
                                                <Mail size={14} />
                                                <input
                                                    type="email"
                                                    value={email}
                                                    onChange={(e) => setEmail(e.target.value)}
                                                    className={styles.accountInput}
                                                />
                                            </div>
                                        </div>

                                        <div className={styles.accountGroup}>
                                            <label className={styles.accountLabel}>Current Password</label>
                                            <div className={styles.accountInputRow}>
                                                <Lock size={14} />
                                                <input
                                                    type="password"
                                                    value={profilePassword}
                                                    onChange={(e) => setProfilePassword(e.target.value)}
                                                    className={styles.accountInput}
                                                />
                                            </div>
                                        </div>

                                        <button type="button" className={styles.accountPrimaryBtn} onClick={handleProfileSave} disabled={profileSaving}>
                                            {profileSaving ? 'Saving...' : 'Update Account'}
                                        </button>
                                        {profileError && <div className={styles.accountError}>{profileError}</div>}
                                        {profileMessage && <div className={styles.accountSuccess}>{profileMessage}</div>}

                                        <div className={styles.accountDivider} />

                                        <div className={styles.accountGroup}>
                                            <label className={styles.accountLabel}>Old Password</label>
                                            <div className={styles.accountInputRow}>
                                                <Lock size={14} />
                                                <input
                                                    type="password"
                                                    value={oldPassword}
                                                    onChange={(e) => setOldPassword(e.target.value)}
                                                    className={styles.accountInput}
                                                />
                                            </div>
                                        </div>

                                        <div className={styles.accountGroup}>
                                            <label className={styles.accountLabel}>New Password</label>
                                            <div className={styles.accountInputRow}>
                                                <Lock size={14} />
                                                <input
                                                    type="password"
                                                    value={newPassword}
                                                    onChange={(e) => setNewPassword(e.target.value)}
                                                    className={styles.accountInput}
                                                />
                                            </div>
                                        </div>

                                        <div className={styles.accountGroup}>
                                            <label className={styles.accountLabel}>Confirm New Password</label>
                                            <div className={styles.accountInputRow}>
                                                <Lock size={14} />
                                                <input
                                                    type="password"
                                                    value={confirmNewPassword}
                                                    onChange={(e) => setConfirmNewPassword(e.target.value)}
                                                    className={styles.accountInput}
                                                />
                                            </div>
                                        </div>

                                        <button type="button" className={styles.accountSecondaryBtn} onClick={handlePasswordSave} disabled={passwordSaving}>
                                            {passwordSaving ? 'Updating...' : 'Change Password'}
                                        </button>
                                        {passwordError && <div className={styles.accountError}>{passwordError}</div>}
                                        {passwordMessage && <div className={styles.accountSuccess}>{passwordMessage}</div>}
                                    </div>
                                )}
                            </div>
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
