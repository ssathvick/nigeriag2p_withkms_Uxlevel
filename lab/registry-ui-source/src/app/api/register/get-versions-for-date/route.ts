import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(req: NextRequest) {
    return proxyToBackend({
        req,
        targetEndpoint: "/register-data/get_versions_for_a_date",
        buildPayload: (body) => ({
            request_payload: {
                register_id: body.register_id,
                internal_record_id: body.internal_record_id,
                tab_id: body.tab_id,
                truncated_created_date: body.truncated_created_date,
            },
        }),
    });
}
