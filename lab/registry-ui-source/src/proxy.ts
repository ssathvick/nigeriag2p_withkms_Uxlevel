import createMiddleware from 'next-intl/middleware';
import { routing } from './i18n/routing';
import { NextRequest } from 'next/server';

export default function middleware(request: NextRequest) {
    const defaultLocale = process.env.DEFAULT_LOCALE || routing.defaultLocale;
    const handleRequest = createMiddleware({
        ...routing,
        defaultLocale: defaultLocale as any
    });

    return handleRequest(request);
}

export const config = {
    matcher: ['/((?!api|_next|.*\\..*).*)']
};
