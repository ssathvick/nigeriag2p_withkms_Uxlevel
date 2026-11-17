import createMiddleware from 'next-intl/middleware';
import { routing } from './i18n/routing';
import { NextRequest, NextResponse } from 'next/server';
import { randomUUID } from 'crypto';
import { isAllowedBrowserRequest } from './shared/security/request-policy';

export default function middleware(request: NextRequest) {
    const requestId = randomUUID();
    const apiRequest = request.nextUrl.pathname.startsWith('/api/');
    const decorate = (response: NextResponse) => {
        response.headers.set('X-Request-ID', requestId);
        response.headers.set('X-Content-Type-Options', 'nosniff');
        response.headers.set('Referrer-Policy', 'same-origin');
        if (apiRequest || request.cookies.has('X-Access-Token') || request.cookies.has('X-ID-Token')) {
            response.headers.set('Cache-Control', 'no-store, private');
        }
        return response;
    };
    if (!isAllowedBrowserRequest(request, process.env.APP_ORIGIN)) {
        return decorate(NextResponse.json({error: 'A same-origin request is required.'}, {status: 403}));
    }
    if (apiRequest) {
        const headers = new Headers(request.headers);
        // Replace client-supplied IDs; do not reflect arbitrary header values.
        headers.set('X-Request-ID', requestId);
        return decorate(NextResponse.next({request: {headers}}));
    }
    const defaultLocale = process.env.DEFAULT_LOCALE || routing.defaultLocale;
    const handleRequest = createMiddleware({
        ...routing,
        defaultLocale: defaultLocale as any
    });

    return decorate(handleRequest(request));
}

export const config = {
    matcher: ['/api/:path*', '/((?!api|_next|.*\\..*).*)']
};
