import { News } from "@/features/news/types";

export async function getNews(
    page: number = 1,
    pageSize: number = 5,
    search: string = ""
): Promise<{ data: News[]; total: number }> {

    const res = await fetch("/portal/api/news", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ page, pageSize, search }),
        cache: "no-cache",
    });

    if (!res.ok) throw new Error("Failed to fetch news");

    return res.json();
}
