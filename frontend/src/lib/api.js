const configuredApiBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim();

const hostedApiBaseUrl = 'https://akhilvenkata24-spam-detect-backend.hf.space';

function isPlaceholderApiBaseUrl(url) {
    if (!url) return true;

    const normalized = url.toLowerCase();
    return (
        normalized.includes('your-backend-domain.com') ||
        normalized.includes('<backend') ||
        normalized.includes('<your-backend-domain>') ||
        normalized.includes('replace-with')
    );
}

const isLocalDevUrl = (url) => {
    if (!url) return false;
    return /^(https?:\/\/)?(localhost|127\.0\.0\.1)(:\d+)?(\/|$)/i.test(url);
};

// Priority:
// 1) Explicit non-local VITE_API_BASE_URL
// 2) Same-origin proxy path during local development
// 3) Hosted backend fallback
const resolvedApiBaseUrl = isPlaceholderApiBaseUrl(configuredApiBaseUrl) || isLocalDevUrl(configuredApiBaseUrl)
    ? (window.location.hostname === 'localhost' ? '' : hostedApiBaseUrl)
    : configuredApiBaseUrl;

export const API_BASE_URL = resolvedApiBaseUrl.replace(/\/$/, '');

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
