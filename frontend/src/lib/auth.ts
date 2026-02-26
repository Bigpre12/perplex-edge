export const setAuthToken = (token: string) => {
    if (typeof window !== 'undefined') {
        localStorage.setItem('perplex_edge_token', token);
    }
};

export const getAuthToken = () => {
    if (typeof window !== 'undefined') {
        return localStorage.getItem('perplex_edge_token');
    }
    return null;
};

export const removeAuthToken = () => {
    if (typeof window !== 'undefined') {
        localStorage.removeItem('perplex_edge_token');
    }
};

export const clearUser = () => {
    if (typeof window !== 'undefined') {
        localStorage.removeItem('perplex_edge_user');
        removeAuthToken();
    }
}

export const setUser = (user: any) => {
    if (typeof window !== 'undefined') {
        localStorage.setItem('perplex_edge_user', JSON.stringify(user));
    }
}

export const getUser = () => {
    if (typeof window !== 'undefined') {
        const user = localStorage.getItem('perplex_edge_user');
        return user ? JSON.parse(user) : null;
    }
    return null;
}

export const logoutUser = () => {
    if (typeof window !== 'undefined') {
        clearUser();
        window.location.reload();
    }
}
