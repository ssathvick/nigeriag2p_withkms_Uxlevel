import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(request: NextRequest) {
    return proxyToBackend({
        req: request,
        targetEndpoint: "/change-requests/check_change_request_sequence",
        buildPayload: (body) => ({
            request_payload: {
                change_request_id: body.change_request_id,
            },
        }),
        transformResponse: (responseBody) => responseBody.response_payload,
    });
}
