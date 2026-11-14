import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function GET(req: NextRequest) {
    return proxyToBackend({
        req,
        targetEndpoint: '/register-data/get_register_summary_data',
        buildPayload: (body) => ({
            pagination_request: undefined,
            request_payload: {},
        })
    });
}
