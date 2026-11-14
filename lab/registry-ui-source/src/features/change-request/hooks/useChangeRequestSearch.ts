import { useCallback, useEffect, useMemo, useState } from 'react';
import { useFetch } from '@/shared/hooks';
import type { ChangeRequest } from '@/features/change-request/types/change-request';

interface UseChangeRequestSearchOptions {
    pageSize?: number;
    initialPage?: number;
    searchText?: string;
    status?: string;
    enabled?: boolean;
}

export function useChangeRequestSearch({
    pageSize,
    initialPage = 1,
    searchText = '',
    status = 'all',
    enabled = true,
}: UseChangeRequestSearchOptions) {
    const [currentPage, setCurrentPage] = useState(initialPage);

    useEffect(() => {
        setCurrentPage(1);
    }, [searchText,status]);

    const { data, loading } = useFetch<any>({
        url: '/api/change-request/search',
        enabled,
        options: {
            method: 'POST',
            body: JSON.stringify({
                current_page: currentPage,
                page_size: pageSize,
                search_text: searchText,
                filter_by: status === "all" ? "" : JSON.stringify({workflow_status:status}),
            }),
        },
    });

    const changeRequests: ChangeRequest[] = data?.records ?? [];
    const paginationInfo = data?.pagination;

    const onPrev = useCallback(
        () => setCurrentPage(p => Math.max(1, p - 1)),
        []
    );

    const onNext = useCallback(() => {
        const totalPages = paginationInfo?.number_of_pages ?? 1;
        setCurrentPage(p => Math.min(totalPages, p + 1));
    }, [paginationInfo]);

    return {
        changeRequests,
        loading,
        currentPage,
        pageSize,
        paginationInfo,
        setCurrentPage,
        onPrev,
        onNext,
    };
}
