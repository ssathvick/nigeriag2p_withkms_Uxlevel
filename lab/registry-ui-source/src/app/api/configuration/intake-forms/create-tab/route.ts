import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(request: NextRequest) {
    return proxyToBackend({
        req: request,
        targetEndpoint: "/intake-form-metadata/create_tab",
        buildPayload: (body) => ({
            pagination_request: undefined,
            request_payload: {
                form_id: body.form_id,
                tab_label: body.tab_label,
                tab_order: body.tab_order,
            },
        }),
    });
}
