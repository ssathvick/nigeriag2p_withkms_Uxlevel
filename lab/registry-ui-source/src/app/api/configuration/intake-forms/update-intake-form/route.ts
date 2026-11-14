import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(request: NextRequest) {
    return proxyToBackend({
        req: request,
        targetEndpoint: "/intake-form-metadata/update_intake_form",
        buildPayload: (body) => ({
            pagination_request: undefined,
            request_payload: {
                form_id: body.form_id,
                form_mnemonic: body.form_mnemonic,
                form_description: body.form_description,
                number_of_verifications: body.number_of_verifications || 0
            },
        }),
    });
}
