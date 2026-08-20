import { NextRequest, NextResponse } from "next/server";

// Target backend for the same-origin /api proxy.
// - Browser requests on http(s)://frontend/api/... are proxied here.
// - In Docker the backend lives at http://backend:8000 (next-compose sets
//   NEXT_PUBLIC_API_URL); locally it defaults to 127.0.0.1:8000.
const INTERNAL_API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

async function proxy(request: NextRequest) {
  const path = request.nextUrl.pathname;
  const targetUrl = `${INTERNAL_API_URL}${path}${request.nextUrl.search}`;

  const response = await fetch(targetUrl, {
    method: request.method,
    headers: {
      ...Object.fromEntries(request.headers),
    },
    body: request.method !== "GET" && request.method !== "HEAD"
      ? await request.text()
      : undefined,
    redirect: "follow",
  });

  return new NextResponse(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: new Headers(response.headers),
  });
}

export { proxy as GET, proxy as POST, proxy as PUT, proxy as PATCH, proxy as DELETE };
