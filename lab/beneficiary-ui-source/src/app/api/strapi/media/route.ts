import { NextResponse } from "next/server";

export async function GET(req: Request) {
    try {
        const { searchParams } = new URL(req.url);
        const url = searchParams.get("url");

        if (!url) {
            return NextResponse.json({ error: "url is required" }, { status: 400 });
        }

        const baseUrl = process.env.STRAPI_API_URL ?? "http://localhost:1337";
        const res = await fetch(`${baseUrl}${url}`);

        if (!res.ok) throw new Error("Failed to fetch media");

        const buffer = await res.arrayBuffer();
        const contentType = res.headers.get("content-type") ?? "image/jpeg";

        return new NextResponse(buffer, {
            headers: { "Content-Type": contentType },
        });
    } catch (err: any) {
        return NextResponse.json({ error: err.message }, { status: 500 });
    }
}
