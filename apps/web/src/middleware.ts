import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const PUBLIC_PATHS = [
    '/login',
    '/signup',
    '/pricing',
    '/api/health',
    '/_next',
    '/favicon',
    '/icon',
    '/manifest',
    '/robots',
    '/api/auth',
];

export function middleware(request: NextRequest) {
    const { pathname } = request.nextUrl;

    // Always allow public paths
    if (PUBLIC_PATHS.some(p => pathname.startsWith(p))) {
        return NextResponse.next();
    }

    // Check for token in cookies
    const token = request.cookies.get('lucrix_token')?.value;

    // No token on a protected route → redirect to login
    if (!token && pathname !== '/') {
        const loginUrl = new URL('/login', request.url);
        loginUrl.searchParams.set('from', pathname);
        return NextResponse.redirect(loginUrl);
    }

    return NextResponse.next();
}

export const config = {
    matcher: ['/((?!.*\\..*|_next).*)', '/', '/(api|trpc)(.*)'],
};
