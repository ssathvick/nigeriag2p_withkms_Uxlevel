import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(req: NextRequest) {
	return proxyToBackend({
		req,
		targetEndpoint: '/register-data/get_section_records',
		buildPayload: (body) => ({
			pagination_request: {
				current_page: body.current_page ?? 1,
				page_size: body.page_size ?? 20,
				sort_by: body.sort_by ?? "",
				filter_by: body.filter_by ?? "",
				search_text: body.search_text ?? ""
			},
			request_payload: {
				subject_register_id: body.register_id,
				subject_record_id: body.internal_record_id,
				section_register_id: body.section_register_id,
			},
		}),
		transformResponse: (responseBody) =>
			responseBody?.response_payload ?? {},
	})
}
