// Force Hugging Face deployment (bypassing any old cached Render environment variables)
export const API_BASE_URL = 'https://akhilvenkata24-spam-detect-backend.hf.space';

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
