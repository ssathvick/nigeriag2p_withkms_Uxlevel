import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(request: NextRequest) {
    return proxyToBackend({
        req: request,
        targetEndpoint: "/ingestion-config/get_semantic_pattern",
        buildPayload: (body) => ({
            pagination_request: {
                current_page: body.current_page ?? 1,
                page_size: body.page_size ?? 20,
                sort_by: body.sort_by ?? "",
                filter_by: body.filter_by ?? "",
                search_text: body.search_text ?? ""
            },
            request_payload: {
                semantic_pattern_id: body.semantic_pattern_id,
                data_model_id: body.data_model_id,
                register_id: body.register_id,
                section_id: body.section_id,
                pattern_for_register: body.pattern_for_register,
                pattern_for_section: body.pattern_for_section,
                key_path_for_business_payload: body.key_path_for_business_payload,
                raw_payload_enricher_class: body.raw_payload_enricher_class,
            }
        }),
        transformResponse: (responseBody) => ({
            ...responseBody?.response_payload,
            semantic_pattern_id: responseBody?.response_payload?.semantic_pattern_id,
            data_model_id: responseBody?.response_payload?.data_model_id,
            data_model_mnemonic: responseBody?.response_payload?.data_model_mnemonic,
            register_id: responseBody?.response_payload?.register_id,
            register_mnemonic: responseBody?.response_payload?.register_mnemonic,
            section_id: responseBody?.response_payload?.section_id,
            section_mnemonic: responseBody?.response_payload?.section_mnemonic,
        }),
    });
}
