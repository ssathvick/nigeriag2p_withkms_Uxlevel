import { NextRequest } from 'next/server';
import { proxyToBackend } from '@/app/api/_lib/backend-proxy';

export async function POST(request: NextRequest) {
    return proxyToBackend({
        req: request,
        targetEndpoint: '/register-data/add_policy',
        buildPayload: (body) => ({
            pagination_request: {
                current_page: body.current_page ?? 1,
                page_size: body.page_size ?? 20,
                sort_by: body.sort_by ?? '',
                filter_by: body.filter_by ?? '',
                search_text: body.search_text ?? '',
            },
            request_payload: {
                policy_mnemonic: body.policy_mnemonic,
                policy_description: body.policy_description ?? '',
                register_id: body.register_id,
                policy_type: body.policy_type,
                policy_filter_expression: body.policy_filter_expression ?? {},
            },
        }),
        transformResponse: (responseBody) => responseBody?.response_payload?.policy,
    });
}
