import createMiddleware from "next-intl/middleware";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

import { routing } from "./i18n/routing";
import { prefixBasePath } from '@/shared/utils/path';


const intlMiddleware = createMiddleware(routing);

export default function middleware(req: NextRequest) {
    const { pathname } = req.nextUrl;

    const segments = pathname.split("/");
    const lang = segments[1] || "en";

    if (pathname.startsWith(`/${lang}/login`)) {
        return intlMiddleware(req);
    }
    if (pathname === `/${lang}`) {
        return intlMiddleware(req);
    }

    const token = req.cookies.get("X-Access-Token");
    if (!token) {
        return NextResponse.redirect(
            new URL(prefixBasePath(`/${lang}/login`), req.url)
        );
    }

    return intlMiddleware(req);
}

export const config = {
    matcher: "/((?!api|trpc|_next|_vercel|.*\\..*).*)",
};
