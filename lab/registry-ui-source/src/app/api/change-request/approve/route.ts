
import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(req: NextRequest) {
    return proxyToBackend({
        req,
        targetEndpoint: "/change-requests/approve_change_request",
        buildPayload: (body) => ({
            request_payload: {
                change_request_id: body.change_request_id,
            }
        })
    });
}
