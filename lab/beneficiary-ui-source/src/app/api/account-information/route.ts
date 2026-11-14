import { NextResponse } from "next/server";
import { strapiServerFetch } from "../_utils/strapiServerFetch";

interface StrapiAccountResponse {
    data: Array<{
        id: number;
        account_info: unknown;
    }>;
}

export async function POST() {
    try {
        const json = await strapiServerFetch<StrapiAccountResponse>(
            "/api/account-informations",
            { populate: "*" }
        );

        const first = json.data[0];

        if (!first) {
            return NextResponse.json({ error: "No account information found" }, { status: 404 });
        }

        return NextResponse.json({
            id: first.id,
            AccountInfo: first.account_info,
        });
    } catch (err: any) {
        return NextResponse.json({ error: err.message }, { status: 500 });
    }
}
