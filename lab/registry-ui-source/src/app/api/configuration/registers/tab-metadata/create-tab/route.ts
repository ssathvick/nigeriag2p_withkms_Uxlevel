import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(request: NextRequest) {
    return proxyToBackend({
        req: request,
        targetEndpoint: "/register-tab-metadata/create_tab",
        buildPayload: (body) => ({
            pagination_request: undefined,
            request_payload: {
                register_id: body.register_id,
                tab_label: body.tab_label,
                tab_order: body.tab_order,
                is_active: body.is_active
            },
        }),
    });
}
