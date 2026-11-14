import { useCallback, useMemo, useState } from 'react';
import { useFetch } from '@/shared/hooks';
import type { ChangeRequest } from '@/features/change-request/types/change-request';

interface UseChangeRequestListOptions {
    pageSize?: number;
    initialPage?: number;
    searchText?: string;
    subjectRecordId?: string;
    subjectRegisterId?: string;
    tabId?: string;
    enabled?: boolean;
}

export function useChangeRequestList({
    pageSize,
    initialPage = 1,
    searchText = '',
    subjectRecordId,
    subjectRegisterId,
    tabId,
    enabled = true,
}: UseChangeRequestListOptions) {
    const [currentPage, setCurrentPage] = useState(initialPage);

    const { data, loading } = useFetch<any>({
        url: '/api/change-request/get/list',
        enabled,
        options: {
            method: 'POST',
            body: JSON.stringify({
                current_page: currentPage,
                page_size: pageSize,
                search_text: searchText,
                subject_register_id: subjectRegisterId,
                subject_record_id: subjectRecordId,
                tab_id: tabId,
            }),
        },
    });

    const changeRequests: ChangeRequest[] = data?.change_requests ?? [];
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
