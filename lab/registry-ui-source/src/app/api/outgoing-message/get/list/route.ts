import { NextRequest, NextResponse } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(req: NextRequest) {
    /*
    return proxyToBackend({
        req,
        targetEndpoint: "/register/search_in_outgoing_messages",
        buildPayload: (body) => ({
            pagination_request: {
                current_page: body.current_page ?? 1,
                page_size: body.page_size ?? 20,
                sort_by: body.sort_by ?? "",
                filter_by: body.filter_by ?? "",
                search_text: body.search_text ?? "",
            },
            request_payload: {},
        }),
        transformResponse: (responseBody) => ({
            messages: responseBody.response_payload ?? [],
            pagination: responseBody.pagination_response,
        }),
    });
    */

    const body = await req.json();

    const currentPage = body.current_page ?? 1;
    const pageSize = body.page_size ?? 10;

    // Mock outgoing messages data
    const rawOutgoingMessages = [
        {
            outgest_id: "1234567890",
            queued_datetime: "2025-10-25 10:32AM",
            source_register: "Birth Registry",
            record_id: "43210",
            source_change_request_id: "12378",

            topic_resolution: "Resolved",
            topic_resolution_datetime: "2025-10-25 10:32AM",
            number_of_topics_resolved: 7,
            topic_names: [
                "Vaccination",
                "Immunization",
                "Birth Registration",
                "Death Registration",
                "Migration",
                "Change of Address",
                "Name Correction",
                "Birth Registration (Double)",
                "Vaccination (Checkup)",
                "Death Record",
            ],
        },
        {
            outgest_id: "0987654321",
            queued_datetime: "2025-11-01 09:15AM",
            source_register: "Health Registry",
            record_id: "98765",
            source_change_request_id: "67890",

            topic_resolution: "Pending",
            topic_resolution_datetime: "2025-11-01 09:20AM",
            number_of_topics_resolved: 3,
            topic_names: ["Health Checkup", "Disease Reporting", "Vaccination"],
        },
    ];

    const totalItems = rawOutgoingMessages.length;
    const totalPages = Math.ceil(totalItems / pageSize);

    const startIndex = (currentPage - 1) * pageSize;
    const endIndex = startIndex + pageSize;

    const paginatedMessages = rawOutgoingMessages.slice(startIndex, endIndex);

    return NextResponse.json({
        messages: paginatedMessages,
        pagination: {
            number_of_items: totalItems,
            number_of_pages: totalPages,
        },
    });
}
