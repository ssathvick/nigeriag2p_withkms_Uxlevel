import { useMemo, useCallback, useEffect } from 'react';
import { useParams, useSearchParams } from 'next/navigation';
import { usePathname, useRouter } from '@/i18n/navigation';
import { notFound } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { useFilters } from '@/features/filter/hooks/useFilters';
import { useFetch } from '@/shared/hooks/useFetch';
import { useRegister } from '@/context/RegisterContext';
import { RegisterRecordsApiResponse } from '@/features/register/types';
import { useRuntimeConfig } from '@/context/RuntimeConfigContext';

export const useRegisterRecords = () => {
    const t = useTranslations();
    const router = useRouter();
    const pathname = usePathname();
    const routeParams = useParams<{ type: string }>();
    const searchParams = useSearchParams();

    const { config } = useRuntimeConfig();
    const pageSize = config.pageSize || 10;

    // Derive current page from URL
    const pageFromUrl = searchParams.get('page');
    const currentPage = pageFromUrl ? Math.max(1, parseInt(pageFromUrl)) : 1;

    const {
        appliedFilters,
        filterBy,
        filterConfig,
        applyFilters,
        removeFilter,
        clearAllFilters,
    } = useFilters("/api/register/filters");

    const registerType = routeParams.type;
    const searchQuery = searchParams.get('search') || "";

    const { currentRegister, loading: loadingRegister } = useRegister();

    // If we've finished loading registers and the requested type didn't match any, 404
    if (!loadingRegister && !currentRegister) {
        notFound();
    }

    const registerId = currentRegister?.register_id;
    const registerTypeLabel = t(registerType) ?? currentRegister?.register_subject;

    const { data: recordsData, loading: isLoadingRecords } = useFetch<RegisterRecordsApiResponse>({
        url: `/api/register/records`,
        enabled: !!registerId,
        options: {
            method: 'POST',
            body: JSON.stringify({
                current_page: currentPage,
                page_size: pageSize,
                sort_by: "",
                filter_by: filterBy,
                search_text: searchQuery,
                register_id: currentRegister?.register_id,
            }),
        },
    });

    const records = recordsData?.records ?? [];
    const paginationInfo = recordsData?.pagination;

    const pagination = useMemo(() => {
        if (!paginationInfo) {
            return {
                pageStart: 0,
                pageEnd: 0,
                total: 0,
            };
        }

        const pageStart = (currentPage - 1) * pageSize + 1;
        const pageEnd = Math.min(
            currentPage * pageSize,
            paginationInfo.number_of_items || 0
        );

        return {
            pageStart,
            pageEnd,
            total: paginationInfo.number_of_items || 0,
        };
    }, [paginationInfo, currentPage, pageSize]);

    const handlePreviousPage = useCallback(() => {
        if (currentPage > 1) {
            const params = new URLSearchParams(searchParams.toString());
            params.set('page', (currentPage - 1).toString());
            router.push(`${pathname}?${params.toString()}`);
        }
    }, [currentPage, searchParams, router, pathname]);

    const handleNextPage = useCallback(() => {
        const totalPages = paginationInfo?.number_of_pages ?? 1;
        if (currentPage < totalPages) {
            const params = new URLSearchParams(searchParams.toString());
            params.set('page', (currentPage + 1).toString());
            router.push(`${pathname}?${params.toString()}`);
        }
    }, [currentPage, paginationInfo, searchParams, router, pathname]);

    const handleSearch = useCallback((searchValue: string) => {
        const params = new URLSearchParams(searchParams.toString());
        if (searchValue.trim()) {
            params.set('search', searchValue.trim());
        } else {
            params.delete('search');
        }
        params.set('page', '1');
        router.push(`${pathname}?${params.toString()}`);
    }, [searchParams, router, pathname]);

    return {
        registerType,
        registerTypeLabel,
        records,
        isLoadingRecords,
        searchQuery,
        pagination,
        handlers: {
            handlePreviousPage,
            handleNextPage,
            handleSearch,
        },
        filters: {
            appliedFilters,
            filterConfig,
            applyFilters,
            removeFilter,
            clearAllFilters,
        }
    };
};
