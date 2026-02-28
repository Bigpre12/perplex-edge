import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

function decodeJwt(token: string) {
    try {
        const parts = token.split('.');
        if (parts.length !== 3) return null;
        // Native atob is available in Next.js Edge Runtime
        const payload = JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')));
        return payload;
    } catch (e) {
        return null;
    }
}

export async function middleware(req: NextRequest) {
    const authCookie = req.cookies.get('sb-access-token') || req.cookies.get('perplex-auth');
    const token = authCookie?.value;

    const isAuthPage = req.nextUrl.pathname.startsWith('/login') || req.nextUrl.pathname.startsWith('/signup');
    const isPublicRoute = (req.nextUrl.pathname === '/' && req.nextUrl.searchParams.has('public')) || req.nextUrl.pathname.startsWith('/results');
    const isApiRoute = req.nextUrl.pathname.startsWith('/api') || req.nextUrl.pathname.startsWith('/_next');

    // Tier-based routes
    const isPremiumRoute = req.nextUrl.pathname.startsWith('/institutional') ||
        req.nextUrl.pathname.startsWith('/sharp-analysis');

    if (isApiRoute || isPublicRoute) {
        return NextResponse.next();
    }

    // Redirect authenticated users away from auth pages
    if (token && isAuthPage) {
        return NextResponse.redirect(new URL('/', req.url));
    }

    // Redirect unauthenticated users to login
    if (!token && !isAuthPage) {
        return NextResponse.redirect(new URL('/login', req.url));
    }

    // Premium Route Protection
    if (token && isPremiumRoute) {
        const payload = decodeJwt(token);
        const tier = payload?.subscription_tier || 'free';

        if (tier !== 'pro' && tier !== 'admin') {
            return NextResponse.redirect(new URL('/checkout?reason=premium_required', req.url));
        }
    }

    return NextResponse.next();
}

export const config = {
    matcher: ['/((?!api|_next/static|_next/image|images|favicon.ico|manifest.json).*)'],
};
