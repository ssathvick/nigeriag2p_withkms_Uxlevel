
import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(req: NextRequest) {
	return proxyToBackend({
		req,
		targetEndpoint: "/change-requests-core-data/approve_change_request_for_core_data",
		buildPayload: (body) => ({
			request_payload: {
				change_request_id: body.change_request_id,
			}
		})
	});
}
