import { useCallback, useMemo, useState } from 'react';
import { useFetch } from '@/shared/hooks';

interface OutgoingMessage {
    outgest_id: string;
    queued_datetime: string;
    source_register: string;
    record_id: string;
    source_change_request_id: string;
    topic_resolution: string;
    topic_resolution_datetime: string;
    number_of_topics_resolved: number;
    topic_names: string[];
}

interface UseOutgoingMessagesListOptions {
    pageSize?: number;
    initialPage?: number;
    searchText?: string;
    enabled?: boolean;
}

export function useOutgoingMessagesList({
    pageSize,
    initialPage = 1,
    searchText = '',
    enabled = true,
}: UseOutgoingMessagesListOptions) {
    const [currentPage, setCurrentPage] = useState(initialPage);

    const { data, loading } = useFetch<any>({
        url: '/api/outgoing-message/get/list',
        enabled,
        options: {
            method: 'POST',
            body: JSON.stringify({
                current_page: currentPage,
                page_size: pageSize,
                search_text: searchText,
            }),
        },
    });

    const messages: OutgoingMessage[] = data?.messages ?? [];
    const paginationInfo = data?.pagination;

    const onPrev = useCallback(() => setCurrentPage(p => Math.max(1, p - 1)), []);

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
