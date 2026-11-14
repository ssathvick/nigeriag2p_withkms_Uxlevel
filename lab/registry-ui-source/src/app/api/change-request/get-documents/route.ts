import { NextRequest } from 'next/server';
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(request: NextRequest) {
    return proxyToBackend({
        req: request,
        targetEndpoint: '/documents/get_change_request_documents',

        buildPayload: (body) => ({
            request_payload: {
                change_request_id: body.change_request_id,
            }
        }),
    });
}
