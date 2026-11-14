"use client";
import { useEffect, useState } from "react";

interface PaginatedResponse<T> {
    response_body: {
        response_payload: T[];
        pagination_response: PaginationData;
    };
}

interface PaginationData {
    number_of_pages: number;
    number_of_items: number;
}

interface PaginationParams {
    currentPage: number;
    pageSize: number;
}

interface PaginatedDataOptions<T> {
    baseUrl?: string;
    currentPage: number;
    pageSize: number;
    fetchFn: (baseUrl: string, params: PaginationParams) => Promise<PaginatedResponse<T>>;
}

interface PaginatedDataReturn<T> {
    data: T[];
    loading: boolean;
    totalPages: number;
    totalItems: number;
}

export function usePaginatedData<T>({
    baseUrl,
    currentPage,
    pageSize = 8,
    fetchFn,
}: PaginatedDataOptions<T>): PaginatedDataReturn<T> {
    const [data, setData] = useState<T[]>([]);
    const [loading, setLoading] = useState(true);
    const [totalPages, setTotalPages] = useState(1);
    const [totalItems, setTotalItems] = useState(0);

    async function fetchData(url: string) {
        try {
            setData([])
            setLoading(true);
            const result = await fetchFn(url, { currentPage, pageSize });

            const list = result?.response_body?.response_payload ?? [];
            const pagination = result?.response_body?.pagination_response ?? {};

            setData(Array.isArray(list) ? list : []);
            setTotalPages(pagination.number_of_pages || 1);
            setTotalItems(pagination.number_of_items || 0);
        } catch (err) {
            console.error("Failed to fetch data:", err);
            setData([]);
            setTotalPages(1);
            setTotalItems(0);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        if (!baseUrl) return;
        fetchData(baseUrl);
    }, [baseUrl, currentPage, pageSize, fetchFn]);

    return { data, loading, totalPages, totalItems };
}
