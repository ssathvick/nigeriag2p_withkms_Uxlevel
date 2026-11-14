import { NextRequest } from 'next/server';
import { proxyToBackend } from '@/app/api/_lib/backend-proxy';

export async function GET(req: NextRequest) {
    return proxyToBackend({
        req,
        targetEndpoint: '/awe/my_task_stats',
        buildPayload: () => ({
            request_payload: {status:'pending'},
        }),
        transformResponse: (responseBody) => responseBody?.response_payload?.data,
    });
}
