import { NextResponse } from "next/server";
import { serverFetch } from "@/app/api/_utils/serverFetch";
import { buildStandardPayload } from "@/shared/utils/payloadBuilder";

export async function POST(req: Request) {
    try {
        const { sparUrl } = await req.json();

        const payload = buildStandardPayload({ pageSize: 100 });
        const data = await serverFetch(
            sparUrl,
            "/dfsp/fetch-banks",
            payload
        );

        return NextResponse.json(data);
    } catch (e: any) {
        return NextResponse.json({ error: e.message }, { status: 500 });
    }
}
