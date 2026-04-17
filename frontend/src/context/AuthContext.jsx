import { createContext, useState, useEffect, useContext, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_BASE_URL, apiUrl } from '../lib/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token') || sessionStorage.getItem('token') || null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    const parseJwtPayload = (jwtToken) => {
        try {
            const base64Url = jwtToken.split('.')[1];
            if (!base64Url) return null;
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            const padded = base64.padEnd(Math.ceil(base64.length / 4) * 4, '=');
            return JSON.parse(atob(padded));
        } catch {
            return null;
        }
    };

    const parseResponseBody = async (res) => {
        const text = await res.text();
        if (!text) {
            return {};
        }

        try {
            return JSON.parse(text);
        } catch {
            return { message: text };
        }
    };

    const logout = useCallback(() => {
        setUser(null);
        setToken(null);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        sessionStorage.removeItem('token');
        sessionStorage.removeItem('user');
        navigate('/login');
    }, [navigate]);

    // Check if token exists on load, restore user details and set auto logout
    useEffect(() => {
        let timeoutId;
        
        if (token) {
            const savedUser = localStorage.getItem('user') || sessionStorage.getItem('user');
            if (savedUser && !user) {
                try {
                    setUser(JSON.parse(savedUser));
                } catch {
                    localStorage.removeItem('user');
                    sessionStorage.removeItem('user');
                    setUser(null);
                }
            }
            
            const tokenData = parseJwtPayload(token);
            if (tokenData && tokenData.exp) {
                const expiresIn = (tokenData.exp * 1000) - Date.now();
                if (expiresIn > 0) {
                    timeoutId = setTimeout(() => {
                        logout();
                    }, expiresIn);
                } else {
                    logout();
                }
            }
        } else if (user) {
            setUser(null);
        }
        setLoading(false);
        
        return () => {
            if (timeoutId) {
                clearTimeout(timeoutId);
            }
        };
    }, [token, user, logout]);

    const login = async (username, password) => {
        try {
            const res = await fetch(apiUrl('/api/auth/login'), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            const data = await parseResponseBody(res);
            
            if (res.ok && data.status === 'success' && data.access_token) {
                setToken(data.access_token);
                setUser(data.user);
                localStorage.setItem('token', data.access_token);
                localStorage.setItem('user', JSON.stringify(data.user || null));
                sessionStorage.setItem('token', data.access_token);
                sessionStorage.setItem('user', JSON.stringify(data.user || null));
                return { success: true };
            } else {
                return { success: false, message: data.message || `Login failed (${res.status})` };
            }
        } catch (err) {
            const target = API_BASE_URL || window.location.origin;
            return { success: false, message: `Server connection failed (${target})` };
        }
    };

    const register = async (username, email, password) => {
        try {
            const res = await fetch(apiUrl('/api/auth/register'), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password })
            });
            const data = await parseResponseBody(res);
            
            if (res.ok && data.status === 'success') {
                return { success: true };
            } else {
                return { success: false, message: data.message || `Registration failed (${res.status})` };
            }
        } catch (err) {
            const target = API_BASE_URL || window.location.origin;
            return { success: false, message: `Server connection failed (${target})` };
        }
    };



    const updateAuthUser = (details) => {
        const newUser = { ...user, ...details };
        setUser(newUser);
        localStorage.setItem('user', JSON.stringify(newUser));
        sessionStorage.setItem('user', JSON.stringify(newUser));
    };

    return (
        <AuthContext.Provider value={{ user, token, loading, login, register, logout, updateAuthUser }}>
            {!loading && children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
