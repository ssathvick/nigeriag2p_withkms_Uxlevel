import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(request: NextRequest) {
	return proxyToBackend({
		req: request,
		targetEndpoint: "/registry-language/update_language",
		buildPayload: (body) => ({
			pagination_request: {
				current_page: body.current_page ?? 1,
				page_size: body.page_size ?? 20,
				sort_by: body.sort_by ?? "",
				filter_by: body.filter_by ?? "",
				search_text: body.search_text ?? ""
			},
			request_payload: {
				language_id: body.language_id,
				language_code: body.language_code,
				language_label: body.language_label,
				language_flag_base64: body.language_flag_base64,
				is_default: body.is_default ?? false,
				language_translation: body.language_translation,
			},
		}),
	});
}
