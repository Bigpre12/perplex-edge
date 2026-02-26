import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export async function middleware(req: NextRequest) {
    // Attempt to read the Supabase Auth cookie or local storage equivalent 
    // In a pure client-side SPA without SSR helpers, the easiest protection is checking for a generic auth pattern.
    // However, since we're using Next.js App Router, we'll implement a basic cookie check.
    // If you need strict verification, you should use @supabase/ssr
    const authCookie = req.cookies.get('sb-access-token');

    // For now, if someone tries to reach /institutional but has no authentication cookie, reroute them.
    // Since we're using the standard client JS setup, let's enforce a softer check or just allow client-side hydration to redirect.
    // Actually, we'll allow client side layout to handle the hard bounce to avoid flash of unauthenticated content,
    // but we can add a basic block here.
    return NextResponse.next();
}

export const config = {
    matcher: ['/institutional/:path*']
};
