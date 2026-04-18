// Force Hugging Face deployment (bypassing any old cached Render environment variables)
export const API_BASE_URL = 'https://akhilvenkata24-spam-detect-backend.hf.space';

export function apiUrl(path) {
    const normalizedPath = path.startsWith('/') ? path : `/${path}`;
    return `${API_BASE_URL}${normalizedPath}`;
}

export async function fetchWithRetry(url, options = {}, retries = 3, backoff = 1000) {
    for (let i = 0; i < retries; i++) {
        try {
            const response = await fetch(url, options);
            return response;
        } catch (error) {
            console.error(`Fetch attempt ${i + 1} failed:`, error.message);
            if (i === retries - 1) throw error; // Rethrow on last attempt
            
            // Wait before next retry (exponential backoff)
            await new Promise((resolve) => setTimeout(resolve, backoff * Math.pow(2, i)));
        }
    }
}
