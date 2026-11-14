import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(request: NextRequest) {
    return proxyToBackend({
        req: request,
        targetEndpoint: "/intake-form-metadata/get_intake_form",
        buildPayload: (body) => ({
            pagination_request: undefined,
            request_payload: {
                form_id: body.form_id,
            },
        }),
    });
}
