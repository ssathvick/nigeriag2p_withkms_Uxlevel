import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(request: NextRequest) {
	return proxyToBackend({
		req: request,
		targetEndpoint: "/register-metadata/add_register_section",
		buildPayload: (body) => ({
			pagination_request: {
				current_page: body.current_page ?? 1,
				page_size: body.page_size ?? 20,
				sort_by: body.sort_by ?? "",
				filter_by: body.filter_by ?? "",
				search_text: body.search_text ?? ""
			},
			request_payload: {
				section_register_id: body.section_register_id,
				register_id: body.register_id,
				tab_id: body.tab_id,
				section_mnemonic: body.section_mnemonic,
				section_description: body.section_description,
				documents_required: body.documents_required,
				no_of_verifications_required: body.no_of_verifications_required,
				auto_approval: body.auto_approval,
				is_list: body.is_list,
				section_ui_schema: body.section_ui_schema,
				is_core_section: body.is_core_section,
				is_primary_section: body.is_primary_section,
				section_order: body.section_order,
				section_weightage: body.section_weightage,

			},
		}),
	});
}
