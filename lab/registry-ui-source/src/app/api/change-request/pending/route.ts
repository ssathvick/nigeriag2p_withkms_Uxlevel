import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(req: NextRequest) {
    return proxyToBackend({
        req,
        targetEndpoint: "/change-requests/get_number_of_pending_change_requests",
        buildPayload: (body) => ({
            request_payload: {
                subject_register_id: body.subject_register_id,
                subject_record_id: body.subject_record_id,
                tab_id: body.tab_id,
            },
        }),
    });
}
