import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(request: NextRequest) {
    return proxyToBackend({
        req: request,
        targetEndpoint: "/input-mechanism-metadata/create_import_file_configuration",
        buildPayload: (body) => ({
            pagination_request: {
                current_page: body.current_page ?? 1,
                page_size: body.page_size ?? 1,
                sort_by: body.sort_by ?? "",
                filter_by: body.filter_by ?? "",
                search_text: body.search_text ?? "",
            },
            request_payload: {
                register_id: body.register_id,
                form_id: body.form_id,
                data_model_id: body.data_model_id,
                import_file_template_mnemonic: body.import_file_template_mnemonic,
                import_file_template_description: body.import_file_template_description ?? "",
            },
        }),
        transformResponse: (responseBody) => {
            const payload = responseBody?.response_payload;
            return Array.isArray(payload) ? payload[0] : payload;
        },
    });
}
