import "server-only";
import { NextRequest, NextResponse } from "next/server";
import { getBackendConfig } from "./backend-config";
import { BackendResponse, RequestBody } from "./backend-types";
import { createBackendRequest } from "./backend-request";
import { requireAuth } from "./requireAuth";

export type PayloadBuilder = (body: any) => RequestBody;
export type ResponseTransformer = (responseBody: any) => any;

interface BackendProxyOptions {
	req: NextRequest;
	targetEndpoint: string; // Backend API endpoint
	buildPayload?: PayloadBuilder;
	transformResponse?: ResponseTransformer; // Transforms backend response for client
	caching?: RequestInit; // this is used for Nextjs caching
	responseHeaders?: HeadersInit; // HTTP headers for client response or caching
	backend?: "default" | "masterdata";
}

const errorCodeMap: Record<string, number> = {
	"G2P-AUT-401": 401,
	"G2P-AUT-403": 403,
	"G2P-AUT-404": 404,
};


export async function proxyToBackend({
	req,
	backend,
	targetEndpoint,
	buildPayload,
	transformResponse,
	caching,
	responseHeaders
}: BackendProxyOptions) {

	const backendConfig = getBackendConfig()
	const auth = requireAuth(req);
	if (auth instanceof NextResponse) return auth;

	try {
		const contentType = req.headers.get("content-type") || "";
		const isFormData = contentType.includes("multipart/form-data");

		let body: any = {};
		if (req.method !== 'GET') {
			if (isFormData) {
				body = await req.formData();
			} else {
				try {
					body = await req.json();
				} catch (e) {
					// ignore JSON parse error for empty body or if already read
				}
			}
		}

		const baseUrl =
			backend === "masterdata"
				? backendConfig.masterdataBackendApiUrl
				: backendConfig.backendApiUrl;

		const backendUrl = `${baseUrl}${targetEndpoint}`;

		const fetchOptions: RequestInit = {
			method: "POST",
			...caching,
		};

		if (isFormData) {
			const { 'content-type': _, 'Content-Type': __, ...cleanHeaders } =
				auth.backendHeaders as Record<string, string>;

			fetchOptions.headers = {
				...cleanHeaders,
			};
			fetchOptions.body = body;
			// When sending FormData, the browser/runtime will automatically set
			// the Content-Type header with the correct boundary.
		}
		else {
			const defaultPayloadBuilder: PayloadBuilder = (b) => ({
				pagination_request: undefined,
				request_payload: b
			});

			const payload = (buildPayload || defaultPayloadBuilder)(body);

			const h = req.headers;
			const host = h.get("x-forwarded-host") || h.get("host");
			const proto = h.get("x-forwarded-proto") || "https";
			const origin = h.get("origin") || `${proto}://${host}`;

			const backendRequest = createBackendRequest(payload, origin);

			// console.log(backendRequest, "backendRequest*********************", backendUrl, "backendUrl*********************")

			fetchOptions.headers = {
				...auth.backendHeaders,
				"Content-Type": "application/json",
			};
			fetchOptions.body = JSON.stringify(backendRequest);
		}

		const response = await fetch(backendUrl, fetchOptions);

		const backendResponse: BackendResponse = await response.json();

		if (backendResponse.response_header?.response_status === 'ERROR') {
			const errorCode = backendResponse.response_header.response_error_code;

			const status = errorCodeMap[errorCode] || 400;

			return NextResponse.json(
				{
					error: backendResponse.response_header.response_error_message,
					code: errorCode,
				},
				{
					status,
					headers: responseHeaders,
				}
			);
		}

		const responseBody = backendResponse.response_body;
		const data = transformResponse
			? transformResponse(responseBody)
			: responseBody?.response_payload;

		return NextResponse.json(data, { headers: responseHeaders });

	} catch (e) {
		return NextResponse.json(
			{ error: e instanceof Error ? e.message : 'Internal Server Error' },
			{ status: 500 }
		);
	}
}
