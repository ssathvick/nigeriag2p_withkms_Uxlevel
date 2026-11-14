import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(request: NextRequest) {
    return proxyToBackend({
        req: request,
        targetEndpoint: "/ingestion-config/create_incoming_key_path",
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
                key_path_for_message_id: body.key_path_for_message_id,
                key_path_for_sender: body.key_path_for_sender,
                key_path_for_signature: body.key_path_for_signature,
                key_path_for_signature_payload: body.key_path_for_signature_payload,
                is_list: body.is_list,
                key_path_for_list_elements: body.key_path_for_list_elements,
            }
        }),
    });
}
