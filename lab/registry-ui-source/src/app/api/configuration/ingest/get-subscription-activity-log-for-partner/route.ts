import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(request: NextRequest) {
    return proxyToBackend({
        req: request,
        targetEndpoint: "/ingestion-config/get_subscription_activity_logs_by_partner",
        buildPayload: (body) => ({
            pagination_request: {
                current_page: body.current_page ?? 1,
                page_size: body.page_size ?? 20,
                sort_by: body.sort_by ?? "",
                filter_by: body.filter_by ?? "",
                search_text: body.search_text ?? ""
            },
            request_payload: {
                is_unsubscribe: body.is_unsubscribe,
                description: body.description,
                partner_id: body.partner_id,
                subscription_url: body.subscription_url,
                registry_callback_url: body.registry_callback_url,
                header: body.header,
                payload: body.payload,
                response: body.response,
            }
        }),
    });
}
