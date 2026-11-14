import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(request: NextRequest) {
    return proxyToBackend({
        req: request,
        targetEndpoint: "/register-data/get_score_contributing_attributes",
        buildPayload: (body) => ({
            pagination_request: {
                current_page:
                    body.current_page ?? body.page ?? body.currentPage ?? 1,
                page_size: body.page_size ?? body.pageSize ?? 20,
                sort_by: body.sort_by ?? "",
                filter_by: body.filter_by ?? "",
                search_text: body.search_text ?? "",
            },
            request_payload: {
                score_definition_id: body.score_definition_id,
            },
        }),
        transformResponse: (responseBody) => ({
            contributingAttributes:
                responseBody?.response_payload?.contributing_attributes ?? [],
            pagination: responseBody?.pagination_response,
        }),
    });
}
