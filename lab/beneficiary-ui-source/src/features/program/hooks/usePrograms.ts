"use client";

import { getAllPrograms, getMyPrograms } from "@/features/program/utils";
import type { Program } from "@/features/program/types";
import { usePbmsUrl } from "@/features/program/hooks";
import { usePaginatedData } from "@/shared/hooks/usePaginatedData";

export function usePrograms(type: "all" | "my", currentPage: number, pageSize = 8) {
    const pbmsUrl = usePbmsUrl();

    const fetchFn = type === "my" ? getMyPrograms : getAllPrograms;

    const result = usePaginatedData<Program>({
        baseUrl: pbmsUrl,
        currentPage,
        pageSize,
        fetchFn,
    });

    return {
        programs: result.data,
        loading: result.loading,
        totalPages: result.totalPages,
        totalItems: result.totalItems,
    };
}
