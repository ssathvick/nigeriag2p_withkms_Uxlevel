import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(request: NextRequest) {
    return proxyToBackend({
        req: request,
        targetEndpoint: "/register-section-metadata/update_section_ui_schema",
        buildPayload: (body) => ({
            pagination_request: undefined,
            request_payload: {
                section_id: body.section_id,
                register_id: body.register_id,
                section_ui_schema: body.section_ui_schema
            },
        }),
    });
}
