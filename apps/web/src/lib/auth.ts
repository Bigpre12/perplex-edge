const TOKEN_KEY = 'lucrix_token';
const USER_KEY = 'lucrix_user';

export const authStorage = {
    saveToken: (token: string) => {
        if (typeof window === 'undefined') return;
        localStorage.setItem(TOKEN_KEY, token);
        // Middleware can only read cookies
        document.cookie = `${TOKEN_KEY}=${token}; path=/; max-age=${60 * 60 * 24 * 7}; SameSite=Lax`;
    },
    getToken: (): string | null => {
        if (typeof window === 'undefined') return null;
        return localStorage.getItem(TOKEN_KEY);
    },
    saveUser: (user: any) => {
        if (typeof window === 'undefined') return;
        localStorage.setItem(USER_KEY, JSON.stringify(user));
    },
    getUser: () => {
        if (typeof window === 'undefined') return null;
        try {
            const u = localStorage.getItem(USER_KEY);
            return u ? JSON.parse(u) : null;
        } catch { return null; }
    },
    clear: () => {
        if (typeof window === 'undefined') return;
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
        document.cookie = `${TOKEN_KEY}=; path=/; max-age=0`;
    },
    isLoggedIn: (): boolean => {
        if (typeof window === 'undefined') return false;
        return !!localStorage.getItem(TOKEN_KEY);
    }
};

// Also keep existing exports for compatibility if needed, but refactor to use authStorage
export const setAuthToken = authStorage.saveToken;
export const getAuthToken = authStorage.getToken;
export const removeAuthToken = () => authStorage.clear();
export const setUser = authStorage.saveUser;
export const getUser = authStorage.getUser;
export const clearUser = authStorage.clear;
export const logoutUser = () => {
    authStorage.clear();
    if (typeof window !== 'undefined') {
        window.location.href = '/login';
    }
};
