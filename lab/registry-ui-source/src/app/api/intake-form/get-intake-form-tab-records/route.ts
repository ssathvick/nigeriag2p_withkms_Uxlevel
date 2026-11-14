import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(request: NextRequest) {
    return proxyToBackend({
        req: request,
        targetEndpoint: "/intake-form-data/get_tab_records",
        buildPayload: (body) => ({
            pagination_request: {
                current_page: body.current_page ?? 1,
                page_size: body.page_size ?? 10,
                sort_by: body.sort_by ?? "",
                filter_by: body.filter_by ?? "",
                search_text: body.search_text ?? "",
            },
            request_payload: {
                submission_id: body.submission_id,
                tab_id: body.tab_id
            },
        }),
        transformResponse: (responseBody) => ({
            section_payloads: responseBody?.response_payload || [],
            pagination: responseBody?.pagination_response,
        }),
    });
}
