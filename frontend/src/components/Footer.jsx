import { useState } from 'react';
import { Shield, X, Mail } from 'lucide-react';
import styles from './Footer.module.css';

export function Footer() {
    const [activeModal, setActiveModal] = useState(null);

    const closeModal = () => setActiveModal(null);

    return (
        <footer className={styles.footer}>
            <div className={styles.container}>
                <div className={styles.copyright}>
                    <Shield size={18} />
                    <span>© 2026 Spam.Detect System. All rights reserved.</span>
                </div>
                <div className={styles.links}>
                    <a href="#" onClick={(e) => { e.preventDefault(); setActiveModal('privacy'); }}>Privacy Policy</a>
                    <a href="#" onClick={(e) => { e.preventDefault(); setActiveModal('terms'); }}>Terms of Service</a>
                    <a href="#" onClick={(e) => { e.preventDefault(); setActiveModal('contact'); }}>Contact Support</a>
                </div>
            </div>

            {activeModal && (
                <div style={{
                    position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', 
                    background: 'rgba(0,0,0,0.85)', display: 'flex', justifyContent: 'center', 
                    alignItems: 'center', zIndex: 9999, backdropFilter: 'blur(5px)'
                }} onClick={closeModal}>
                    <div 
                        style={{
                            background: 'var(--background)', border: '1px solid var(--border)',
                            borderRadius: '12px', padding: '2rem', maxWidth: '500px', width: '90%',
                            boxShadow: '0 20px 40px rgba(0,0,0,0.8)', overflowY: 'auto', maxHeight: '80vh',
                            position: 'relative'
                        }}
                        onClick={e => e.stopPropagation()}
                    >
                        <button onClick={closeModal} style={{ position: 'absolute', top: '15px', right: '15px', background: 'none', border: 'none', color: 'var(--muted-foreground)', cursor: 'pointer' }}><X size={24} /></button>
                        
                        {activeModal === 'privacy' && (
                            <div>
                                <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1rem', color: 'var(--foreground)' }}>Privacy Policy</h2>
                                <p style={{ color: 'var(--muted-foreground)', lineHeight: '1.6', marginBottom: '1rem' }}>Your data is strictly localized. Messages sent for analysis are aggressively sanitized. We explicitly do not sell or archive your metadata. All localized data instances expire according to your backend threshold settings.</p>
                                <p style={{ color: 'var(--muted-foreground)', lineHeight: '1.6' }}>We adhere to high-grade AES compliance for cloud transit telemetry.</p>
                            </div>
                        )}

                        {activeModal === 'terms' && (
                            <div>
                                <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1rem', color: 'var(--foreground)' }}>Terms of Service</h2>
                                <p style={{ color: 'var(--muted-foreground)', lineHeight: '1.6', marginBottom: '1rem' }}>By running this terminal, you agree not to utilize the threat scoring APIs for automated malicious enumeration. Limits are strictly capped by your operator clearance rating (Rate Limiting algorithms).</p>
                                <p style={{ color: 'var(--muted-foreground)', lineHeight: '1.6' }}>System administrators reserve the right to revoke API token privileges for any abusive queries generated against the AI engine.</p>
                            </div>
                        )}

                        {activeModal === 'contact' && (
                            <div>
                                <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1.5rem', color: 'var(--foreground)' }}>
                                    <Mail size={24} style={{ color: 'var(--primary)' }} /> System Operators
                                </h2>
                                <p style={{ color: 'var(--muted-foreground)', marginBottom: '1.5rem' }}>Direct network inquiries to the core architectural development team:</p>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                    <div style={{ background: 'rgba(255,255,255,0.05)', padding: '1rem', borderRadius: '8px' }}>
                                        <div style={{ fontWeight: 'bold', color: 'var(--foreground)' }}>Akhil</div>
                                        <a href="mailto:akhilnakarikanti@gmail.com" style={{ color: 'var(--primary)', textDecoration: 'none', fontSize: '0.9rem' }}>akhilnakarikanti@gmail.com</a>
                                    </div>
                                    <div style={{ background: 'rgba(255,255,255,0.05)', padding: '1rem', borderRadius: '8px' }}>
                                        <div style={{ fontWeight: 'bold', color: 'var(--foreground)' }}>Neerush</div>
                                        <a href="mailto:neerushbuchi07@gmail.com" style={{ color: 'var(--primary)', textDecoration: 'none', fontSize: '0.9rem' }}>neerushbuchi07@gmail.com</a>
                                    </div>
                                    <div style={{ background: 'rgba(255,255,255,0.05)', padding: '1rem', borderRadius: '8px' }}>
                                        <div style={{ fontWeight: 'bold', color: 'var(--foreground)' }}>Gowtham</div>
                                        <a href="mailto:gowthamch5828@gmail.com" style={{ color: 'var(--primary)', textDecoration: 'none', fontSize: '0.9rem' }}>gowthamch5828@gmail.com</a>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </footer>
    );
}
