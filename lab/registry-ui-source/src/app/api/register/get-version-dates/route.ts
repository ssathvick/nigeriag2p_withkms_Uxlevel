import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(req: NextRequest) {
    return proxyToBackend({
        req,
        targetEndpoint: "/register-data/get_version_dates",
        buildPayload: (body) => ({
            request_payload: {
                register_id: body.register_id,
                internal_record_id: body.internal_record_id,
                tab_id: body.tab_id,
            },
        }),
        transformResponse: (responseBody) => ({
            dates:
                responseBody?.response_payload?.version_dates ?? [],
        }),
    });
}
