
import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(req: NextRequest) {
	return proxyToBackend({
		req,
        backend: "masterdata",
		targetEndpoint: "/attributes/get_attribute_values",
        transformResponse: body => body?.response_payload?.attribute_values ?? [],
		buildPayload: (body) => ({
			pagination_request: {
				current_page: body.current_page ?? 1,
				page_size: body.page_size ?? 20,
				sort_by: body.sort_by ?? "",
				filter_by: body.filter_by ?? "",
				search_text: body.search_text ?? "",
			},
			request_payload: {
				attribute_id: body.attribute_id,
				parent_value_id: body.parent_id ?? ""
			}
		})
	});
}
