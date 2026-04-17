import { createContext, useState, useEffect, useContext, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token') || null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    const logout = useCallback(() => {
        setUser(null);
        setToken(null);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        navigate('/login');
    }, [navigate]);

    // Check if token exists on load, restore user details and set auto logout
    useEffect(() => {
        let timeoutId;
        
        if (token) {
            const savedUser = localStorage.getItem('user');
            if (savedUser) {
                setUser(JSON.parse(savedUser));
            }
            
            try {
                const tokenData = JSON.parse(atob(token.split('.')[1]));
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
            } catch (e) {
                // Ignore token decoding errors
            }
        }
        setLoading(false);
        
        return () => {
            if (timeoutId) {
                clearTimeout(timeoutId);
            }
        };
    }, [token, logout]);

    const login = async (username, password) => {
        try {
            const res = await fetch((import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000') + '/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            const data = await res.json();
            
            if (res.ok && data.status === 'success') {
                setToken(data.access_token);
                setUser(data.user);
                localStorage.setItem('token', data.access_token);
                localStorage.setItem('user', JSON.stringify(data.user));
                navigate('/dashboard');
                return { success: true };
            } else {
                return { success: false, message: data.message || "Invalid credentials" };
            }
        } catch (err) {
            return { success: false, message: "Server connection failed" };
        }
    };

    const register = async (username, email, password) => {
        try {
            const res = await fetch((import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000') + '/api/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password })
            });
            const data = await res.json();
            
            if (res.ok && data.status === 'success') {
                return { success: true };
            } else {
                return { success: false, message: data.message || "Registration failed" };
            }
        } catch (err) {
            return { success: false, message: "Server connection failed" };
        }
    };



    const updateAuthUser = (details) => {
        const newUser = { ...user, ...details };
        setUser(newUser);
        localStorage.setItem('user', JSON.stringify(newUser));
    };

    return (
        <AuthContext.Provider value={{ user, token, loading, login, register, logout, updateAuthUser }}>
            {!loading && children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
