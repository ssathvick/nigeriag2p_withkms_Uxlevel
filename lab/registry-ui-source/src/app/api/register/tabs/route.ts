import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(req: NextRequest) {
    return proxyToBackend({
        req,
        targetEndpoint: '/register-metadata/get_register_tabs',
        buildPayload: (body) => ({
            pagination_request: {
                current_page: body.current_page ?? 1,
                page_size: body.page_size ?? 20,
                sort_by: body.sort_by ?? "",
                filter_by: body.filter_by ?? "",
                search_text: body.search_text ?? "",
            },
            request_payload: {
                register_id: body.register_id ?? "",
                used_for_new_intake_form: body.used_for_new_intake_form ?? false
            }
        }),

        caching: {
            next: { revalidate: 3600 }
        } as RequestInit,

        responseHeaders: {
            'Cache-Control': 'public, max-age=3600, s-maxage=3600'
        }
    });
}
