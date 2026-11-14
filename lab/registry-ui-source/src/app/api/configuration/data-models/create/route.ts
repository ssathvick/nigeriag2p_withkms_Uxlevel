import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(req: NextRequest) {
    return proxyToBackend({
        req,
        targetEndpoint: "/data-model/create_data_model",
        buildPayload: (body) => ({
            pagination_request: {
                current_page: body.current_page ?? 1,
                page_size: body.page_size ?? 20,
                sort_by: body.sort_by ?? "",
                filter_by: body.filter_by ?? "",
                search_text: body.search_text ?? ""
            },
            request_payload: {
                data_model_id: body.data_model_id,
                data_model_mnemonic: body.data_model_mnemonic,
                pattern_for_data_model: body.pattern_for_data_model,
                response_template_file_id: body.response_template_file_id ?? "",
                is_active: body.is_active ?? true,
            },
        }),
    });
}
