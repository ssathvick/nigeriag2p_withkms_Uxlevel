import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(request: NextRequest) {
    return proxyToBackend({
        req: request,
        targetEndpoint: "/registry-config/update_registry_configuration",
        buildPayload: (body) => ({
            pagination_request: {
                current_page: body.current_page ?? 1,
                page_size: body.page_size ?? 20,
                sort_by: body.sort_by ?? "",
                filter_by: body.filter_by ?? "",
                search_text: body.search_text ?? ""
            },
            request_payload: {
                configuration_id: body.configuration_id,
                registry_name: body.registry_name,
                registry_logo: body.registry_logo,
                registry_theme_id: body.registry_theme_id,
                registry_language_id: body.registry_language_id,
            },
        }),
    });
}
