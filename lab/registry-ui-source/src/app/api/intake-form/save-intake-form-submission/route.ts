import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(request: NextRequest) {
    return proxyToBackend({
        req: request,
        targetEndpoint: "/intake-form-data/save_intake_form_submission",
        buildPayload: (body) => ({
            pagination_request: undefined,
            request_payload: {
                submission_id: body.submission_id,
                section_id: body.section_id,
                section_payload: body.section_payload,
                section_register_id: body.section_register_id,
                form_id: body.form_id,
                register_id: body.register_id,
                created_by: body.created_by,
            },
        }),
    });
}
