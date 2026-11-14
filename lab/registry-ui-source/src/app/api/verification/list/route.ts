import { NextRequest } from 'next/server';
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(request: NextRequest) {
    return proxyToBackend({
        req: request,
        targetEndpoint: '/verifications/get_verifications',
        buildPayload: (body) => ({
            pagination_request: {
                current_page: body.current_page ?? 1,
                page_size: body.page_size ?? 20,
                sort_by: body.sort_by ?? "",
                filter_by: body.filter_by ?? "",
                search_text: body.search_text ?? "",
            },
            request_payload: {
                change_request_id: body.change_request_id ?? "",
                submission_id: body.submission_id ?? ""
            },
        }),
        transformResponse: (responseBody) => ({
            verifications: responseBody.response_payload.verifications,
            pagination: responseBody.pagination_response,
        }),
    });
}
