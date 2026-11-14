import { useMemo } from 'react';

export function usePagination({
    totalItems,
    currentPage,
    pageSize,
    currentCount,
}: {
    totalItems: number;
    currentPage: number;
    pageSize: number;
    currentCount: number;
}) {
    return useMemo(() => {
        const pageStart =
            totalItems === 0 ? 0 : (currentPage - 1) * pageSize + 1;

        const pageEnd =
            (currentPage - 1) * pageSize + currentCount;

        return {
            pageStart,
            pageEnd: Math.min(pageEnd, totalItems),
            total: totalItems,
        };
    }, [totalItems, currentPage, pageSize, currentCount]);
}
