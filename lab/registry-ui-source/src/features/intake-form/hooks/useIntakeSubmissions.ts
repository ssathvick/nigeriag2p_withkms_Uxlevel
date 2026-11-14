import { useCallback, useMemo } from "react";
import { useFetch } from "@/shared/hooks/useFetch";

export const useIntakeSubmissions = (
    registerId?: string,
    params?: {
        searchText?: string;
        status?: string;
        currentPage?: number;
        pageSize?: number;
    }
) => {
    const fetchOptions = useMemo(
        () => ({
            method: "POST" as const,
            body: JSON.stringify({
                register_id: registerId,
                search_text: params?.searchText,
                filter_by: params?.status && params.status !== "all" ? JSON.stringify({workflow_status:params.status}) : "",
                current_page: params?.currentPage,
                page_size: params?.pageSize,
            }),
        }),
        [registerId, params?.searchText, params?.currentPage, params?.pageSize, params?.status],
    );

    const { data, loading, execute } = useFetch<any>({
        url: "/api/intake-form/search-in-intake-form-submission",
        options: fetchOptions,
        enabled: !!registerId,
    });
    const submissions = data?.submissions;
    const paginationInfo = data?.pagination;

    const refetch = useCallback(async () => {
        if (!registerId) return;
        await execute("/api/intake-form/search-in-intake-form-submission", fetchOptions);
    }, [registerId, execute, fetchOptions]);

    return {
        submissions,
        paginationInfo,
        loading,
        refetch,
    };
};
