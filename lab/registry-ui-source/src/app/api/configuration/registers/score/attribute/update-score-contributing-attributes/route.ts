import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(request: NextRequest) {
    return proxyToBackend({
        req: request,
        targetEndpoint: "/register-data/update_score_contributing_attribute",
        buildPayload: (body) => ({
            pagination_request: undefined,
            request_payload: {
                contributing_attribute_id: body.contributing_attribute_id,
                attribute_name: body.attribute_name,
                attribute_computation_required:
                    body.attribute_computation_required ?? false,
                attribute_computation_value:
                    body.attribute_computation_value ?? {},
                attribute_weight:
                    body.attribute_weight ?? body.attribute_weightage ?? 0,
            },
        }),
        transformResponse: (responseBody) =>
            responseBody?.response_payload?.contributing_attribute,
    });
}
