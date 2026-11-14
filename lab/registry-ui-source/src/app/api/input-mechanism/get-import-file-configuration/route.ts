import { NextRequest } from 'next/server';
import { proxyToBackend } from '@/app/api/_lib/backend-proxy';

export async function POST(request: NextRequest) {
    return proxyToBackend({
        req: request,
        targetEndpoint: '/input-mechanism-metadata/get_import_file_configuration_for_register',
        buildPayload: (body) => ({
            pagination_request: {
                current_page: body.current_page ?? 1,
                page_size: body.page_size ?? 20,
                sort_by: body.sort_by ?? '',
                filter_by: body.filter_by ?? '',
                search_text: body.search_text ?? '',
            },
            request_payload: {
                register_id: body.register_id,
            },
        }),
        transformResponse: (responseBody) => ({
            import_file_configurations: responseBody?.response_payload || [],
            pagination: responseBody?.pagination_response,
        }),
    });
}
