import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(request: NextRequest) {
    return proxyToBackend({
        req: request,
        targetEndpoint: "/register-data/get_score_definitions",
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
                register_id: body.register_id,
            },
        }),
        transformResponse: (responseBody) => ({
            scoreDefinitions:
                responseBody?.response_payload?.score_definitions ?? [],
            pagination: responseBody?.pagination_response,
        }),
    });
}
