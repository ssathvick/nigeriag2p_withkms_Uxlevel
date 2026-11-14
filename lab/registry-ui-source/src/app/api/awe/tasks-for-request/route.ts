import { NextRequest } from 'next/server';
import { proxyToBackend } from '@/app/api/_lib/backend-proxy';

export async function POST(request: NextRequest) {
    return proxyToBackend({
        req: request,
        targetEndpoint: '/awe/list_my_tasks',
        buildPayload: (body) => ({
            request_payload: {
                request_id: body.request_id,
                page: body.page ?? 1,
                page_size: body.page_size ?? 100,
            },
        }),
        transformResponse: (responseBody) => {
            const data = responseBody?.response_payload?.data;
            const items = data?.items ?? [];
            return {
                tasks: items,
                total: data?.total ?? items.length,
            };
        },
    });
}
