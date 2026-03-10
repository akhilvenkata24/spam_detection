import { Outlet } from 'react-router-dom';
import { Navbar } from '../components/Navbar';
import { Footer } from '../components/Footer';
import styles from './RootLayout.module.css';

export function RootLayout() {
    return (
        <div className={styles.layout}>
            <Navbar />
            <main className={styles.main}>
                <Outlet />
            </main>
            <Footer />
        </div>
    );
}
