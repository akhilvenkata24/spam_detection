const configuredApiBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim();

const localDevApiBaseUrl = 'http://127.0.0.1:5000';
const hostedApiBaseUrl = 'https://akhilvenkata24-spam-detect-backend.hf.space';

// Priority:
// 1) Explicit VITE_API_BASE_URL
// 2) Local backend when running on localhost
// 3) Hosted backend fallback
const defaultApiBaseUrl = window.location.hostname === 'localhost'
    ? localDevApiBaseUrl
    : hostedApiBaseUrl;

export const API_BASE_URL = (configuredApiBaseUrl || defaultApiBaseUrl).replace(/\/$/, '');

export function apiUrl(path) {
    const normalizedPath = path.startsWith('/') ? path : `/${path}`;
    return `${API_BASE_URL}${normalizedPath}`;
}

export async function fetchWithRetry(url, options = {}, retries = 10, backoff = 2000) {
    for (let i = 0; i < retries; i++) {
        try {
            // Bust browser CORS preflight cache by appending a timestamp
            const separator = url.includes('?') ? '&' : '?';
            const cacheBustedUrl = `${url}${separator}cb=${Date.now()}_${i}`;
            
            const response = await fetch(cacheBustedUrl, options);
            return response;
        } catch (error) {
            console.warn(`Fetch attempt ${i + 1} failed:`, error.message);
            if (i === retries - 1) throw error; // Rethrow on last attempt
            
            // Wait before next retry (cap exponential backoff at 10 seconds to allow for 1-2 min total sleep-wake duration)
            const waitTime = Math.min(backoff * Math.pow(1.5, i), 10000);
            await new Promise((resolve) => setTimeout(resolve, waitTime));
        }
    }
}
