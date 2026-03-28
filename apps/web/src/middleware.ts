import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

const PUBLIC_PATHS = ['/login', '/signup', '/pricing', '/api', '/forgot-password', '/reset-password', '/results']

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  const isPublic = PUBLIC_PATHS.some(p => pathname.startsWith(p))

  // Look for our specific session token (perplex_edge_token is the primary key)
  const token = request.cookies.get('perplex_edge_token')?.value || request.cookies.get('lucrix_token')?.value || request.cookies.get('auth-token')?.value

  // Redirect unauthenticated users to login
  if (!isPublic && !token) {
    return NextResponse.redirect(new URL(`/login?from=${pathname}`, request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
}
