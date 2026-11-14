import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(request: NextRequest) {
	return proxyToBackend({
		req: request,
		targetEndpoint: "/register-metadata/edit_register_tab",
		buildPayload: (body) => ({
			pagination_request: {
				current_page: body.current_page ?? 1,
				page_size: body.page_size ?? 20,
				sort_by: body.sort_by ?? "",
				filter_by: body.filter_by ?? "",
				search_text: body.search_text ?? ""
			},
			request_payload: {
				tab_id: body.tab_id,
				register_id: body.register_id,
				tab_label: body.tab_label ?? "",
				tab_order: body.tab_order ?? 0,
				used_for_new_intake_form: body.used_for_new_intake_form,
				no_of_verifications_required: body.no_of_verifications_required ?? 0,
				intake_form_name: body.intake_form_name ?? "",
				intake_form_description: body.intake_form_description ?? "",
				intake_form_auto_approve: body.intake_form_auto_approve ?? false,
				is_active: body.is_active ?? true
			},
		}),
	});
}
