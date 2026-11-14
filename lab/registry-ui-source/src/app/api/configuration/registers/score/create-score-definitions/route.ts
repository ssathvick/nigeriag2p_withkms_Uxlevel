import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(request: NextRequest) {
    return proxyToBackend({
        req: request,
        targetEndpoint: "/register-data/create_score_definition",
        buildPayload: (body) => ({
            pagination_request: undefined,
            request_payload: {
                register_id: body.register_id,
                score_type: body.score_type,
            },
        }),
        transformResponse: (responseBody) =>
            responseBody?.response_payload?.score_definition,
    });
}
