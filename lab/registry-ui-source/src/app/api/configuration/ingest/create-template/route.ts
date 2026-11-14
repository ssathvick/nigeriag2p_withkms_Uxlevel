import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(req: NextRequest) {
    return proxyToBackend({
        req,
        targetEndpoint: "/ingestion-config/create_template",
        buildPayload: (body) => ({
            pagination_request: {
                current_page: body.current_page ?? 1,
                page_size: body.page_size ?? 20,
                sort_by: body.sort_by ?? "",
                filter_by: body.filter_by ?? "",
                search_text: body.search_text ?? ""
            },
            request_payload: {
                register_id: body.register_id,
                data_model_id: body.data_model_id,
                template_file_id: body.template_file_id ?? "",
                jsonld_expansion_required: body.jsonld_expansion_required ?? false
            },
        }),
    });
}
