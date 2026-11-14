import { NextRequest } from 'next/server';
import { proxyToBackend } from '@/app/api/_lib/backend-proxy';

export async function POST(request: NextRequest) {
    return proxyToBackend({
        req: request,
        targetEndpoint: '/input-mechanism-metadata/create_vc_configuration',
        buildPayload: (body) => ({
            pagination_request: {
                current_page: body.current_page ?? 1,
                page_size: body.page_size ?? 1,
                sort_by: body.sort_by ?? '',
                filter_by: body.filter_by ?? '',
                search_text: body.search_text ?? '',
            },
            request_payload: {
                register_id: body.register_id,
                intake_form_id: body.intake_form_id,
                data_model_id: body.data_model_id,
                vc_mnemonic: body.vc_mnemonic,
                descriptor_schema: body.descriptor_schema ?? {},
            },
        }),
        transformResponse: (responseBody) => {
            const payload = responseBody?.response_payload;
            return Array.isArray(payload) ? payload[0] : payload;
        },
    });
}
