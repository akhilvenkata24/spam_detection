// Force Hugging Face deployment (bypassing any old cached Render environment variables)
export const API_BASE_URL = 'https://akhilvenkata24-spam-detect-backend.hf.space';

export function apiUrl(path) {
    const normalizedPath = path.startsWith('/') ? path : `/${path}`;
    return `${API_BASE_URL}${normalizedPath}`;
}
