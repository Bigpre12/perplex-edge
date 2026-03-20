import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Auth is bypassed — all routes are publicly accessible.
// To re-enable auth, uncomment the token check block below.
export function middleware(request: NextRequest) {
    return NextResponse.next();

    // --- ORIGINAL AUTH GATE (DISABLED) ---
    // const PUBLIC_PATHS = [
    //     '/login', '/signup', '/pricing', '/api/health',
    //     '/_next', '/favicon', '/icon', '/manifest', '/robots', '/api/auth',
    // ];
    // const { pathname } = request.nextUrl;
    // if (PUBLIC_PATHS.some(p => pathname.startsWith(p))) return NextResponse.next();
    // const token = request.cookies.get('lucrix_token')?.value;
    // if (!token && pathname !== '/') {
    //     const loginUrl = new URL('/login', request.url);
    //     loginUrl.searchParams.set('from', pathname);
    //     return NextResponse.redirect(loginUrl);
    // }
    // return NextResponse.next();
}

export const config = {
    matcher: ['/((?!.*\\..*|_next).*)', '/', '/(api|trpc)(.*)'],
};
