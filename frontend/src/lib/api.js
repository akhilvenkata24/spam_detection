const fallbackUrl = 'https://akhilvenkata24-spam-detect-backend.hf.space';
const envBase = (import.meta.env.VITE_API_BASE_URL || fallbackUrl).trim().replace(/\/+$/, '');

// Prefer an explicit deployment URL when provided.
// Otherwise use the hugging face fallback.
export const API_BASE_URL = envBase;

export function apiUrl(path) {
    const normalizedPath = path.startsWith('/') ? path : `/${path}`;
    return `${API_BASE_URL}${normalizedPath}`;
}
