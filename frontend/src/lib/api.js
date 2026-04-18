const envBase = (import.meta.env.VITE_API_BASE_URL || '').trim().replace(/\/+$/, '');

// Prefer an explicit deployment URL when provided.
// Otherwise use same-origin requests and let Vite proxy handle local development.
export const API_BASE_URL = envBase || '';

export function apiUrl(path) {
    const normalizedPath = path.startsWith('/') ? path : `/${path}`;
    return `${API_BASE_URL}${normalizedPath}`;
}
