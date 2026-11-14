import { NextRequest } from 'next/server';
import { proxyToBackend } from '@/app/api/_lib/backend-proxy';

export async function POST(req: NextRequest) {
    return proxyToBackend({
        req,
        targetEndpoint: '/awe-policy-config/delete_awe_policy_configuration',
        buildPayload: (body) => ({
            pagination_request: {
                current_page: body.current_page ?? 1,
                page_size: body.page_size ?? 20,
                sort_by: body.sort_by ?? '',
                filter_by: body.filter_by ?? '',
                search_text: body.search_text ?? '',
            },
            request_payload: {
                awe_policy_config_id: body.awe_policy_config_id,
            },
        }),
    });
}
