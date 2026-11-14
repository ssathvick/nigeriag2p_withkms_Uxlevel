import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(request: NextRequest) {
    return proxyToBackend({
        req: request,
        targetEndpoint: "/intake-form-data/delete_intake_form_submission",
        buildPayload: (body) => ({
            pagination_request: undefined,
            request_payload: {
                submission_id: body.submission_id,
            },
        }),
    });
}
