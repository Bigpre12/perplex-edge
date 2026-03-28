export const TOKEN_STORAGE_KEY = 'perplex_edge_token';
export const USER_STORAGE_KEY = 'perplex_edge_user';

export function handleUnauthorized(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(TOKEN_STORAGE_KEY);
  localStorage.removeItem(USER_STORAGE_KEY);
  
  // Guard against infinite redirects if already on login
  if (!window.location.pathname.startsWith('/login')) {
    window.location.href = '/login?expired=true';
  }
}
