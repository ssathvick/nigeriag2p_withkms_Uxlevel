import { NextResponse } from "next/server";
import { serverFetch } from "../../_utils/serverFetch";
import { buildStandardPayload } from "@/shared/utils/payloadBuilder";

export async function POST(req: Request) {
    try {
        const { sparUrl, transactionId, linkRequest } = await req.json();

        const payload = buildStandardPayload({
            currentPage: 1,
            pageSize: 1,
            sortBy: "",
            filterBy: "",
            searchText: "",
            extraPayload: {
                transaction_id: transactionId,
                link_request: linkRequest,
            },
        });

        const data = await serverFetch(sparUrl, "/mapper/link", payload);
        return NextResponse.json(data);
    } catch (err: any) {
        return NextResponse.json(
            { error: err.message },
            { status: 500 }
        );
    }
}
