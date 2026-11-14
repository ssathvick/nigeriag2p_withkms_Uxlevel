import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(request: NextRequest) {
	return proxyToBackend({
		req: request,
		targetEndpoint: "/change-requests-core-data/create_change_request_for_core_data",
		buildPayload: (body) => ({
			pagination_request: {
				current_page: body.current_page ?? 1,
				page_size: body.page_size ?? 20,
				sort_by: body.sort_by ?? "",
				filter_by: body.filter_by ?? "",
				search_text: body.search_text ?? ""
			},
			request_payload: {
				register_id: body.register_id,
				register_mnemonic: body.register_mnemonic,
				section_register_id: body.section_register_id,
				tab_id: body.tab_id,
				section_id: body.section_id,
				internal_record_id: body.internal_record_id,
				edit_action: body.edit_action,
				change_payload: body.section_records,
				documents: body.documents,
			},
		}),
	});
}
