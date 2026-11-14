import { NextRequest } from 'next/server';
import { proxyToBackend } from '@/app/api/_lib/backend-proxy';
import { scopeScopedIds } from '@/features/configuration/awe-policy-config/scopePayload';

export async function POST(req: NextRequest) {
    return proxyToBackend({
        req,
        targetEndpoint: '/awe-policy-config/update_awe_policy_configuration',
        buildPayload: (body) => {
            const { intake_form_id, section_id } = scopeScopedIds(body);
            return {
                pagination_request: {
                    current_page: body.current_page ?? 1,
                    page_size: body.page_size ?? 20,
                    sort_by: body.sort_by ?? '',
                    filter_by: body.filter_by ?? '',
                    search_text: body.search_text ?? '',
                },
                request_payload: {
                    awe_policy_config_id: body.awe_policy_config_id,
                    policy_scope: body.policy_scope ?? null,
                    register_id: body.register_id ?? null,
                    intake_form_id,
                    section_id,
                    policy_type: body.policy_type ?? null,
                    policy_key: body.policy_key ?? null,
                    context_field_names: body.context_field_names ?? null,
                },
            };
        },
    });
}
