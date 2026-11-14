import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(request: NextRequest) {
    return proxyToBackend({
        req: request,
        targetEndpoint: "/register-metadata/create_register",
        buildPayload: (body) => ({
            pagination_request: {
                current_page: body.current_page ?? 1,
                page_size: body.page_size ?? 20,
                sort_by: body.sort_by ?? "",
                filter_by: body.filter_by ?? "",
                search_text: body.search_text ?? ""
            },
            request_payload: {
                register_mnemonic: body.register_mnemonic,
                register_description: body.register_description,
                master_register_id: body.master_register_id,
                register_purpose: body.register_purpose,
                register_rank: body.register_rank,
                register_icon: body.register_icon,
                dedup_is_enabled: body.dedup_is_enabled,
                dedup_threshold_score: body.dedup_threshold_score,
                functional_id_generation_required: body.functional_id_generation_required,
                completion_score_required: body.completion_score_required,
            },

        }),
    });
}
