import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(request: NextRequest) {
    return proxyToBackend({
        req: request,
        targetEndpoint: "/register-section-metadata/get_section",
        buildPayload: (body) => ({
            pagination_request: {
                current_page: body.current_page ?? 1,
                page_size: body.page_size ?? 20,
                sort_by: body.sort_by ?? "",
                filter_by: body.filter_by ?? "",
                search_text: body.search_text ?? "",
            },
            request_payload: {
                section_id: body.section_id,
                register_id: body.register_id
            },
        }),
        transformResponse: (responseBody) => ({
            section: responseBody?.response_payload,
            pagination: responseBody?.pagination_response,
        }),
    });
}
