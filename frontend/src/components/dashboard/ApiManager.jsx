import { useState } from 'react';
import { Copy, RefreshCw, Check } from 'lucide-react';
import styles from './Dashboard.module.css';

export function ApiManager() {
    const [apiKey, setApiKey] = useState("sk_live_51M3m...92xP");
    const [copied, setCopied] = useState(false);

    const handleCopy = () => {
        navigator.clipboard.writeText(apiKey);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const handleRegenerate = () => {
        // Mock regenerate
        setApiKey("sk_live_" + Math.random().toString(36).substring(2, 18));
        setCopied(false);
    };

    return (
        <div className={styles.apiCard}>
            <h3 className={styles.sectionTitle}>API Integration</h3>
            <p className={styles.sectionDesc}>
                Use this key in your mobile application to send messages for analysis.
            </p>
            <div className={styles.apiKeyContainer}>
                <code className={styles.apiKey}>
                    {apiKey}
                </code>
                <button
                    onClick={handleCopy}
                    className={styles.iconBtn}
                    title="Copy Key"
                >
                    {copied ? <Check size={16} className={styles.textSuccess} /> : <Copy size={16} />}
                </button>
                <button
                    onClick={handleRegenerate}
                    className={styles.iconBtn}
                    title="Regenerate Key"
                >
                    <RefreshCw size={16} />
                </button>
            </div>
            <div className={styles.endpointBox}>
                <p className={styles.endpointText}>
                    Endpoint: <span className={styles.textAmber}>POST https://api.spamdetect.com/v1/analyze</span>
                </p>
            </div>
        </div>
    )
}
