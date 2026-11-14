import {NextRequest,NextResponse} from 'next/server';
import {requireAuth} from '../../_lib/requireAuth';
export async function POST(req:NextRequest){
 const auth=requireAuth(req);if(auth instanceof NextResponse)return auth;
 const response=await fetch(`${process.env.NSIPA_REGISTRATION_URL || 'https://g2p.wverve.in/registration'}/api/registry/offline-setup`,{method:'POST',headers:auth.backendHeaders,cache:'no-store'});
 if(!response.ok)return NextResponse.json({error:response.status===403?'Your role cannot provision field capture.':'Field setup is temporarily unavailable.'},{status:response.status});
 return NextResponse.json(await response.json(),{headers:{'Cache-Control':'no-store, private'}});
}
