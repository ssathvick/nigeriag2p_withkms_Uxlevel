import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(request: NextRequest) {
    return proxyToBackend({
        req: request,
        targetEndpoint: "/register-tab-metadata/update_section",
        buildPayload: (body) => ({
            pagination_request: undefined,
            request_payload: {
                tab_section_id: body.tab_section_id,
                section_id: body.section_id,
                section_order: body.section_order,
            },
        }),
    });
}
