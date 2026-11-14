import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(req: NextRequest) {
    return proxyToBackend({
        req,
        targetEndpoint: '/register-metadata/get_register_schema',
        buildPayload: (body) => ({
            pagination_request: undefined,
            request_payload: {
                register_id: body.register_id,
            },
        }),
    });
}
