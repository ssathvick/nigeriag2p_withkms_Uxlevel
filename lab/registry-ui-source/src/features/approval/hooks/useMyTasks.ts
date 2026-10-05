import { useEffect, useMemo, useState } from 'react';
import { useFetch } from '@/shared/hooks/useFetch';
import { ApprovalTask } from '@/features/approval/types/approval';

interface UseMyTasksOptions {
    artifactType?: string;
    searchText?: string;
    pageSize?: number;
    initialPage?: number;
}

export const useMyTasks = ({
    artifactType,
    searchText = '',
    pageSize = 25,
    initialPage = 1,
}: UseMyTasksOptions) => {
    const [currentPage, setCurrentPage] = useState(initialPage);

    useEffect(() => {
        setCurrentPage(1);
    }, [searchText, artifactType]);

    const options = useMemo(
        () => ({
            method: 'POST' as const,
            body: JSON.stringify({
                artifact_type: artifactType,
                search_text: searchText || undefined,
                page: currentPage,
                page_size: pageSize,
            }),
        }),
        [artifactType, searchText, currentPage, pageSize],
    );

    const { data, loading } = useFetch<{
        items: ApprovalTask[];
        total: number;
        pages: number;
    }>({
        url: '/api/awe/my-tasks',
        options,
    });

    return {
        tasks: data?.items ?? [],
        total: data?.total ?? 0,
        pages: data?.pages ?? 1,
        loading,
        currentPage,
        setCurrentPage,
    };
};
