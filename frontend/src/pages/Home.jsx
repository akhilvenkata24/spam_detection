import { useState } from 'react';
import { Loader2 } from 'lucide-react';
import { AnalysisResult } from '../components/AnalysisResult';
import { useAuth } from '../context/AuthContext';
import { apiUrl } from '../lib/api';
import styles from './Home.module.css';

export function Home() {
    const { token } = useAuth();
    const [text, setText] = useState("");
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [result, setResult] = useState(null);

    const handleAnalyze = async () => {
        if (!text.trim()) return;

        setIsAnalyzing(true);
        try {
            const headers = {
                'Content-Type': 'application/json',
            };
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }

            const res = await fetch(apiUrl('/analyze'), {
                method: 'POST',
                headers: headers,
                body: JSON.stringify({
                    text: text,
                    source: "Web"
                })
            });
            const data = await res.json();

            if (data.status === 'success') {
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
                alert("Error analyzing threat: " + data.message);
            }
        } catch (error) {
            console.error(error);
            alert("Failed to connect to the analysis engine. Make sure the backend is running.");
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
                </>
            ) : (
                <AnalysisResult result={result} onReset={() => { setResult(null); setText(""); }} />
            )}
        </div>
    );
}
