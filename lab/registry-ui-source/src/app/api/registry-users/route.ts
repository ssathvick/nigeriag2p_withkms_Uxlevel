import {NextRequest,NextResponse} from 'next/server';
import {requireAuth} from '../_lib/requireAuth';
async function handle(req:NextRequest){
 const auth=requireAuth(req);if(auth instanceof NextResponse)return auth;
 const r=await fetch(`${process.env.NSIPA_REGISTRATION_URL || 'https://g2p.wverve.in/registration'}/api/registry/users`,{method:req.method,headers:auth.backendHeaders,body:req.method==='POST'?JSON.stringify(await req.json()):undefined,cache:'no-store'});
 if(!r.ok&&r.headers.get('content-type')?.includes('html'))return NextResponse.json({error:r.status===403?'Administrator access is required.':'User administration is temporarily unavailable.'},{status:r.status});
 return NextResponse.json(await r.json(),{status:r.status,headers:{'Cache-Control':'no-store, private'}});
}
export const GET=handle;export const POST=handle;
