"use client";

import { useEffect, useState } from "react";
import { getNews } from "@/features/news/utils";
import { News } from "@/features/news/types";
import { useRuntimeConfig } from "@/context/RuntimeConfigContext";

export function useNews(page = 1, limit = 3, search = "") {
    const [news, setNews] = useState<News[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [total, setTotal] = useState(0);
    const { strapiApiUrl } = useRuntimeConfig();

    async function fetchNews(baseUrl: string) {
        try {
            setNews([]);
            setLoading(true);
            setError(null);

            const { data, total } = await getNews(page, limit, search);
            setNews(data);
            setTotal(total)
        } catch (err) {
            setError("Failed to load news");
            setNews([]);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        if (!strapiApiUrl) return;

        fetchNews(strapiApiUrl);
    }, [page, limit, search, strapiApiUrl]);

    return {
        news,
        total,
        loading,
        error,
    };
}
