import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(request: NextRequest) {
    return proxyToBackend({
        req: request,
        targetEndpoint: "/register-data/delete_score_contributing_attribute",
        buildPayload: (body) => ({
            pagination_request: undefined,
            request_payload: {
                contributing_attribute_id: body.contributing_attribute_id,
            },
        }),
    });
}
