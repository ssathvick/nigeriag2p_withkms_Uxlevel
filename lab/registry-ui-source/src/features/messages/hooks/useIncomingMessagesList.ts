import { useCallback, useEffect, useMemo, useState } from 'react';
import { useFetch } from '@/shared/hooks';
import { IncomingMessage } from '@/features/messages/types';

interface UseIncomingMessagesListOptions {
    pageSize?: number;
    initialPage?: number;
    searchText?: string;
    subjectRecordId?: string;
    subjectRegisterId?: string;
    tabId?: string;
    enabled?: boolean;
}

export function useIncomingMessagesList({
    pageSize,
    initialPage = 1,
    searchText,
    subjectRecordId,
    subjectRegisterId,
    tabId,
    enabled = true,
}: UseIncomingMessagesListOptions) {
    const [currentPage, setCurrentPage] = useState(initialPage);

    useEffect(() => {
        setCurrentPage(1);
    }, [searchText]);

    const { data, loading } = useFetch<any>({
        url: '/api/incoming-message/get/list',
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

    const messages: IncomingMessage[] = data?.messages ?? [];
    const paginationInfo = data?.pagination;

    const onPrev = useCallback(() => {
        setCurrentPage(p => Math.max(1, p - 1));
    }, []);

    const onNext = useCallback(() => {
        const totalPages = paginationInfo?.number_of_pages ?? 1;
        setCurrentPage(p => Math.min(totalPages, p + 1));
    }, [paginationInfo]);

    return {
        messages,
        loading,
        currentPage,
        pageSize,
        paginationInfo,
        setCurrentPage,
        onPrev,
        onNext,
    };
}
