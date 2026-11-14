import { NextRequest, NextResponse } from 'next/server';
import { requireAuth } from '../_lib/requireAuth';
import { getBackendConfig } from '../_lib/backend-config';

export async function GET(req: NextRequest) {
    const auth = requireAuth(req);
    if (auth instanceof NextResponse) return auth;
    const backendConfig = getBackendConfig()
    const iamUrl = `${backendConfig.iamUrl}${"/auth/get_logged_in_user"}`;

    const res = await fetch(iamUrl, {
        method: 'GET',
        headers: auth.backendHeaders,
        cache: 'no-store',
    });

    const data = await res.json();
    if (res.ok) {
        // IAM has validated this token. This hint controls presentation; the API enforces scope.
        const claims = JSON.parse(Buffer.from(auth.accessToken.split('.')[1], 'base64url').toString());
        const roles: string[] = claims.resource_access?.['register-staff-portal']?.roles || [];
        const scopes: Record<string,string> = {'Registry Field Agent':'field','Registry First Reviewer':'level1','Registry Second Reviewer':'level2','Registry Officer':'officer','Registry Administrator':'admin'};
        const matches = [...new Set(roles.filter(r=>scopes[r]).map(r=>scopes[r]))];
        data.registry_scope = matches.length===1 ? matches[0] : 'denied';
    }
    return NextResponse.json(data, { status: res.status });
}
