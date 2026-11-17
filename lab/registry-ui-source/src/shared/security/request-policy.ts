/** Browser request checks only. IAM and the native API remain the authority for access. */
type RequestDetails = {method: string; url: string; headers: Headers};

function originOf(value: string): string | null {
    try {
        const url = new URL(value);
        return ['http:', 'https:'].includes(url.protocol) && !url.username && !url.password
            ? url.origin : null;
    } catch { return null; }
}

export function applicationOrigin(req: RequestDetails, configuredOrigin?: string): string | null {
    if (configuredOrigin) return originOf(configuredOrigin);
    const url = new URL(req.url);
    // The edge proxy must overwrite Host and X-Forwarded-Proto. Never use an
    // incoming X-Forwarded-Host as an additional trusted browser origin.
    const host = req.headers.get('host') || url.host;
    const protocol = req.headers.get('x-forwarded-proto') || url.protocol.slice(0, -1);
    if (!['http', 'https'].includes(protocol) || /[\s,/@\\?#]/.test(host)) return null;
    return originOf(`${protocol}://${host}`);
}

export function isAllowedBrowserRequest(req: RequestDetails, configuredOrigin?: string): boolean {
    if (['GET', 'HEAD', 'OPTIONS'].includes(req.method.toUpperCase())) return true;
    const site = req.headers.get('sec-fetch-site');
    if (site === 'cross-site') return false;
    const expected = applicationOrigin(req, configuredOrigin);
    if (!expected) return false;
    const origin = req.headers.get('origin');
    if (origin !== null) return originOf(origin) === expected;
    const referer = req.headers.get('referer');
    if (referer !== null) return originOf(referer) === expected;
    if (site) return site === 'same-origin';
    // Existing non-browser JSON API clients have no Fetch Metadata/Origin.
    // Cross-origin browsers cannot send JSON without a CORS preflight; this
    // application does not grant cross-origin credentialed API access.
    const type = req.headers.get('content-type')?.split(';')[0].trim().toLowerCase();
    return type === 'application/json';
}
