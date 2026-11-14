import { NextResponse } from "next/server";
import { serverFetch } from "@/app/api/_utils/serverFetch";
import { buildStandardPayload } from "@/shared/utils/payloadBuilder";

export async function POST(req: Request) {
    try {
        const { sparUrl, bankId } = await req.json();

        const payload = buildStandardPayload({
            pageSize: 100,
            extraPayload: { bank_id: bankId },
        });

        const data = await serverFetch(
            sparUrl,
            "/dfsp/fetch-branches",
            payload
        );

        return NextResponse.json(data);
    } catch (e: any) {
        return NextResponse.json({ error: e.message }, { status: 500 });
    }
}
