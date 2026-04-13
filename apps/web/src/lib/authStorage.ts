export const TOKEN_STORAGE_KEY = 'perplex_edge_token';
export const USER_STORAGE_KEY = 'perplex_edge_user';

export function handleUnauthorized(): void {
  if (typeof window === 'undefined') return;
  // Only redirect if the user actually had a token (was previously authenticated)
  // This prevents redirect loops when visiting the site unauthenticated
  const hadToken = localStorage.getItem(TOKEN_STORAGE_KEY) || localStorage.getItem('accessToken');
  localStorage.removeItem(TOKEN_STORAGE_KEY);
  localStorage.removeItem(USER_STORAGE_KEY);
  localStorage.removeItem('accessToken');

  // Guard against infinite redirects if already on login, and only redirect if had a token
  if (hadToken && !window.location.pathname.startsWith('/login')) {
    window.location.href = '/login?expired=true';
  }
}
