import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/request'

const PUBLIC_PATHS = ['/', '/login', '/signup', '/pricing', '/api']

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  const isPublic = PUBLIC_PATHS.some(p => pathname.startsWith(p))
  
  // Look for our specific session token
  const token = request.cookies.get('lucrix_token')?.value || request.cookies.get('auth-token')?.value

  // Use temporary bypass for now as requested
  // if (!isPublic && !token) {
  //   return NextResponse.redirect(new URL(`/login?from=${pathname}`, request.url))
  // }
  
  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
}
