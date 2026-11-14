'use client';

import { WorkflowFilters } from '@/components/shared/Workflow';
import { useCallback } from 'react';
import { useLocale, useTranslations } from 'next-intl';
import { useSearchParams } from 'next/navigation';
import { useRouter } from '@/i18n/navigation';

import { TopBar } from '@/components/shared';
import { ChangeRequestList, ChangeRequestSkeleton } from '@/features/change-request/components';
import { useChangeRequestSearch } from '@/features/change-request/hooks/useChangeRequestSearch';
import { usePagination } from '@/shared/hooks';
import { useRuntimeConfig } from '@/context/RuntimeConfigContext';

export default function ChangeRequestPage() {
    const locale = useLocale();
    const router = useRouter();
    const t = useTranslations();
    const { config } = useRuntimeConfig();

    const searchParams = useSearchParams();
    const searchQuery = searchParams.get('search') || undefined;
    const pageSize = config.pageSize || 10;

    const {
        changeRequests,
        loading,
        currentPage,
        paginationInfo,
        onPrev,
        onNext,
    } = useChangeRequestSearch({
        pageSize,
        searchText: searchQuery,
        status: searchParams.get("status") || "all",
    });

    const { pageStart, pageEnd, total } = usePagination({
        totalItems: paginationInfo?.number_of_items ?? 0,
        currentPage,
        pageSize,
        currentCount: changeRequests.length,
    });


    const handleSearch = useCallback((searchValue: string) => {
        const params = new URLSearchParams(searchParams.toString());
        if (searchValue.trim()) {
            params.set('search', searchValue.trim());
        } else {
            params.delete('search');
        }
        router.push(`/change-request?${params.toString()}`);
    }, [searchParams]);

    return (
        <div className="min-h-screen mx-auto bg-secondary-first">
            <TopBar
                breadcrumb={[{ label: t("change_request") }]}
                showSearch
                searchValue={searchQuery || ''}
                searchPlaceholder={t('search')}
                onSearch={handleSearch}
                pxClass='px-0.5'
                showFilters={false}
                showPagination
                pageStart={pageStart}
                pageEnd={pageEnd}
                total={total}
                onPrev={onPrev}
                onNext={onNext}
            />

            <WorkflowFilters />
            <div className="px-7.5">
                {loading ? (
                    <div className="space-y-4">
                        {[...Array(3)].map((_, i) => (
                            <ChangeRequestSkeleton key={i} />
                        ))}
                    </div>
                ) : changeRequests.length === 0 ? (
                    <div className="text-sm text-secondary-third text-center py-6">
                        {t('no_change_requests_found')}
                    </div>
                ) : (
                    <ChangeRequestList
                        changeRequests={changeRequests}
                        getDetailsUrl={changeRequest =>
                            `/${locale}/change-request/${changeRequest.change_request_id}`
                        }
                    />
                )}
            </div>
        </div>
    );
}
