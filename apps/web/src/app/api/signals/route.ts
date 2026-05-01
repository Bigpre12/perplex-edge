import { NextRequest, NextResponse } from 'next/server'
const BACKEND = process.env.BACKEND_URL

export async function GET(req: NextRequest) {
  const query = new URL(req.url).searchParams.toString()
  try {
    const res = await fetch(
      `${BACKEND}/api/signals${query ? '?' + query : ''}`,
      { headers: { 'Content-Type': 'application/json' }, next: { revalidate: 30 } }
    )
    const data = await res.json()
    return NextResponse.json(data)
  } catch {
    return NextResponse.json({ error: 'Backend unavailable', data: [] }, { status: 503 })
  }
}
