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

    let data;
    try { data = await res.json(); }
    catch {
        const status = [401, 403].includes(res.status) ? res.status : 502;
        return NextResponse.json({error: status === 401 ? 'Please sign in again.' :
            status === 403 ? 'Your role cannot access this application.' : 'The identity service is temporarily unavailable.'},
            {status, headers: {'Cache-Control': 'no-store, private'}});
    }
    if (res.ok) {
        // IAM has validated this token. This hint controls presentation; the API enforces scope.
        let claims;
        try { claims = JSON.parse(Buffer.from(auth.accessToken.split('.')[1], 'base64url').toString()); }
        catch { return NextResponse.json({error: 'Please sign in again.'}, {status: 401, headers: {'Cache-Control': 'no-store, private'}}); }
        const claimRoles = claims?.resource_access?.['register-staff-portal']?.roles;
        const roles: string[] = Array.isArray(claimRoles) ? claimRoles.filter((role): role is string => typeof role === 'string') : [];
        const scopes: Record<string,string> = {'Registry Field Agent':'field','Registry First Reviewer':'level1','Registry Second Reviewer':'level2','Registry Officer':'officer','Registry Administrator':'admin'};
        const matches = [...new Set(roles.filter(r=>scopes[r]).map(r=>scopes[r]))];
        data.registry_scope = matches.length===1 ? matches[0] : 'denied';
        data.registry_actor_id = typeof claims.sub === 'string' ? claims.sub : undefined;
        data.data_imports_enabled = Boolean(process.env.DATA_IMPORTS_DB);
    }
    return NextResponse.json(data, { status: res.status, headers: {'Cache-Control': 'no-store, private'} });
}
