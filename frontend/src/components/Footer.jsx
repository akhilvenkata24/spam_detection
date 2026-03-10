import { Shield } from 'lucide-react';
import styles from './Footer.module.css';

export function Footer() {
    return (
        <footer className={styles.footer}>
            <div className={styles.container}>
                <div className={styles.copyright}>
                    <Shield size={18} />
                    <span>© 2026 Spam.Detect System. All rights reserved.</span>
                </div>
                <div className={styles.links}>
                    <a href="#">Privacy Policy</a>
                    <a href="#">Terms of Service</a>
                    <a href="#">Contact Support</a>
                </div>
            </div>
        </footer>
    );
}
