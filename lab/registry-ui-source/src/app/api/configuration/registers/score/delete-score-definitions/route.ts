import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(request: NextRequest) {
    return proxyToBackend({
        req: request,
        targetEndpoint: "/register-data/delete_score_definition",
        buildPayload: (body) => ({
            pagination_request: undefined,
            request_payload: {
                score_definition_id: body.score_definition_id,
            },
        }),
    });
}
