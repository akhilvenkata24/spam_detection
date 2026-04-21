import { useState } from 'react';
import { Loader2, ShieldAlert } from 'lucide-react';
import { AnalysisResult } from '../components/AnalysisResult';
import { useAuth } from '../context/AuthContext';
import { apiUrl, fetchWithRetry } from '../lib/api';
import styles from './Home.module.css';

export function Home() {
    const { token } = useAuth();
    const [text, setText] = useState("");
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [result, setResult] = useState(null);

    const handleAnalyze = async () => {
        if (!text.trim()) return;

        setIsAnalyzing(true);
        setResult(null);
        try {
            const headers = {
                'Content-Type': 'application/json',
            };
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }

            const requestBody = JSON.stringify({
                text: text,
                source: "Web"
            });

            const parseBody = async (res) => {
                const textBody = await res.text();
                if (!textBody) return {};
                try {
                    return JSON.parse(textBody);
                } catch {
                    return { message: textBody };
                }
            };

            const runAnalyze = async (requestHeaders) => {
                const res = await fetchWithRetry(apiUrl('/analyze'), {
                    method: 'POST',
                    headers: requestHeaders,
                    body: requestBody
                }, 3, 1000);
                const data = await parseBody(res);
                return { res, data };
            };

            let { res, data } = await runAnalyze(headers);

            // If auth token is stale or rejected for this request, retry once anonymously.
            if ((res.status === 401 || res.status === 422) && headers.Authorization) {
                const anonymousHeaders = { 'Content-Type': 'application/json' };
                ({ res, data } = await runAnalyze(anonymousHeaders));
            }

            if (res.ok && data.status === 'success') {
                setResult({
                    score: data.risk_score,
                    flags: data.details.found_triggers || [],
                    details: [
                        { label: "Verdict", value: data.verdict.toUpperCase(), risk: data.verdict !== 'safe' },
                        { label: "Reason", value: data.reason, risk: false },
                        { label: "ML Probability", value: `${(data.details.ml_probability * 100).toFixed(1)}%`, risk: data.details.ml_probability > 0.5 },
                        { label: "Heuristic Score", value: data.details.heuristic_score, risk: data.details.heuristic_score > 50 },
                        { label: "URLs Risk", value: data.details.url_risk !== null ? `${data.details.url_risk}/100` : "N/A", risk: data.details.url_risk > 0 }
                    ]
                });
            } else {
                const message = data.message || `Analysis failed (${res.status})`;
                alert("Error analyzing threat: " + message);
            }
        } catch (error) {
            console.error(error);
            alert(`Failed to connect to the analysis engine: ${error.message}`);
        } finally {
            setIsAnalyzing(false);
        }
    };

    return (
        <div className={styles.container}>
            {!result ? (
                <>
                    <div className={styles.hero}>
                        <h1 className={styles.title}>
                            ADVANCED THREAT FORENSICS
                        </h1>
                        <p className={styles.subtitle}>
                            A Content-Centric Threat Intelligence System. Analyze suspicious messages with zero-trust AI forensics.
                        </p>
                    </div>

                    <div className={styles.scannerWrapper}>
                        <div className={styles.scannerBox}>
                            <textarea
                                value={text}
                                onChange={(e) => setText(e.target.value)}
                                className={styles.textarea}
                                placeholder="Paste suspicious text, SMS, or email content here to scan..."
                                disabled={isAnalyzing}
                            />
                            <div className={styles.controls}>
                                <div className={styles.counter}>
                                    {text.length} CONST / {text.split(" ").length} TOKENS
                                </div>
                                <button
                                    onClick={handleAnalyze}
                                    disabled={isAnalyzing || !text}
                                    className={styles.analyzeBtn}
                                >
                                    {isAnalyzing ? (
                                        <><Loader2 className={styles.spinner} size={16} /> ANALYZING...</>
                                    ) : (
                                        "ANALYZE THREAT"
                                    )}
                                </button>
                            </div>
                        </div>
                    </div>

                    <div className={styles.mobileSyncCard}>
                        <div className={styles.mobileSyncHeader}>
                            <h2 className={styles.mobileSyncTitle}>Mobile Sync App</h2>
                            <p className={styles.mobileSyncDesc}>
                                Scan this QR placeholder to download the mobile app and sync your SMS inbox with this dashboard.
                            </p>
                        </div>
                        <div className={styles.mobileSyncBody}>
                            <div className={styles.qrPlaceholder} aria-label="QR placeholder for mobile app download">
                                <img src="/Spam.Detect Android Application.svg" alt="Mobile app download QR placeholder" className={styles.qrImage} />
                            </div>
                            <div className={styles.mobileSyncCaution}>
                                <ShieldAlert size={18} />
                                <p>
                                    Caution: pause Play Protect before installation. You can turn it back on after setup is complete.
                                    Installation may be blocked due to sensitive-info access checks.
                                </p>
                            </div>
                        </div>
                    </div>
                </>
            ) : (
                <AnalysisResult result={result} onReset={() => { setResult(null); setText(""); }} />
            )}
        </div>
    );
}
