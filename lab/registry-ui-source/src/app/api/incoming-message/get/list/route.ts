import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(req: NextRequest) {
    return proxyToBackend({
        req,
        targetEndpoint: "/ingestion-data/search_in_ingestion_data",
        buildPayload: (body) => ({
            pagination_request: {
                current_page: body.current_page ?? 1,
                page_size: body.page_size ?? 20,
                sort_by: body.sort_by ?? "",
                filter_by: body.filter_by ?? "",
                search_text: body.search_text ?? "",
            },
            request_payload: {
                subject_register_id: body.subject_register_id,
                subject_record_id: body.subject_record_id,
                tab_id: body.tab_id,
            },
        }),
        transformResponse: (responseBody) => ({
            messages: responseBody.response_payload ?? [],
            pagination: responseBody.pagination_response,
        }),
    });
}
