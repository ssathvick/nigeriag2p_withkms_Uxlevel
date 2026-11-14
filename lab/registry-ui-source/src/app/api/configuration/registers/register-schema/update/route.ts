import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(req: NextRequest) {
    return proxyToBackend({
        req,
        targetEndpoint: '/register-metadata/update_register_schema',
        buildPayload: (body) => ({
            pagination_request: undefined,
            request_payload: {
                register_id: body.register_id,
                deduplicate_schema: body.deduplicate_schema,
                search_result_schema: body.search_result_schema,
                filter_schema: body.filter_schema,
            },
        }),
    });
}
