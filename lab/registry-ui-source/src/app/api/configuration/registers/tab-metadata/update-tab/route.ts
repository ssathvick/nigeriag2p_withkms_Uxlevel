import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(request: NextRequest) {
    return proxyToBackend({
        req: request,
        targetEndpoint: "/register-tab-metadata/update_tab",
        buildPayload: (body) => ({
            pagination_request: undefined,
            request_payload: {
                tab_id: body.tab_id,
                tab_label: body.tab_label,
                tab_order: body.tab_order,
                is_active: body.is_active
            },
        }),
    });
}
