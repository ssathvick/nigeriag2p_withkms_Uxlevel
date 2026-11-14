import { NextResponse } from "next/server";
import { News } from "@/features/news/types";
import { strapiServerFetch } from "../_utils/strapiServerFetch";

interface StrapiNewsResponse {
    data: Array<{
        id: number;
        title: string;
        description: string;
        date: string;
        image?: { url: string; alternativeText: string | null };
    }>;
    meta: { pagination: { total: number } };
}

export async function POST(req: Request) {
    try {
        const { page = 1, pageSize = 5, search = "" } = await req.json();

        const json = await strapiServerFetch<StrapiNewsResponse>("/api/allnews", {
            pagination: { page, pageSize },
            sort: ["createdAt:desc"],
            filters: search
                ? {
                    $or: [
                        { title: { $containsi: search } },
                        { description: { $containsi: search } },
                    ],
                }
                : undefined,
            populate: {
                image: { fields: ["url", "alternativeText"] },
            },
        });

        const data: News[] = json.data.map((item) => ({
            id: item.id,
            title: item.title,
            description: item.description,
            date: item.date,
            image: item.image
                ? {
                    url: item.image.url,
                    alternativeText: item.image.alternativeText ?? "",
                }
                : undefined,
        }));

        return NextResponse.json({ data, total: json.meta.pagination.total });
    } catch (err: any) {
        return NextResponse.json({ error: err.message }, { status: 500 });
    }
}
