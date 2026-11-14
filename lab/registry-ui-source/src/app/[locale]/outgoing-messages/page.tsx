'use client';

import { useCallback } from 'react';
import { useTranslations } from 'next-intl';
import { useSearchParams } from 'next/navigation';
import { useRouter } from '@/i18n/navigation';

import { TopBar } from '@/components/shared';
import { SelectedFilters } from '@/features/filter/components';
import { useFilters } from '@/features/filter/hooks/useFilters';
import { OutgoingMessageCardSkeleton, OutgoingMessageList } from '@/features/messages/components';
import { useOutgoingMessagesList } from '@/features/messages/hooks';
import { usePagination } from '@/shared/hooks';
import { useRuntimeConfig } from '@/context/RuntimeConfigContext';

export default function OutgoingMessagesPage() {
    const router = useRouter();
    const t = useTranslations();
    const { config } = useRuntimeConfig();

    const searchParams = useSearchParams();
    const searchQuery = searchParams.get('search') || undefined;
    const pageSize = config.pageSize || 10;

    const {
        appliedFilters,
        filterBy,
        filterConfig,
        applyFilters,
        removeFilter,
        clearAllFilters,
    } = useFilters("/api/register/filters");
    // change thr url once api is ready

    const {
        messages,
        loading,
        currentPage,
        paginationInfo,
        onPrev,
        onNext,
    } = useOutgoingMessagesList({
        pageSize,
        searchText: searchQuery,
    });

    const { pageStart, pageEnd, total } = usePagination({
        totalItems: paginationInfo?.number_of_items ?? 0,
        currentPage,
        pageSize,
        currentCount: messages.length,
    });

    const handleSearch = useCallback((searchValue: string) => {
        const params = new URLSearchParams(searchParams.toString());
        if (searchValue.trim()) {
            params.set('search', searchValue.trim());
        } else {
            params.delete('search');
        }
        router.push(`/outgoing-messages?${params.toString()}`);
    }, [searchParams]);

    return (
        <div className="min-h-screen mx-auto bg-secondary-first">
            <TopBar
                breadcrumb={[{ label: t('outgoing_messages') }]}
                showFilters
                showPagination
                pageStart={pageStart}
                pageEnd={pageEnd}
                total={total}
                onPrev={onPrev}
                onNext={onNext}
                onApplyFilters={applyFilters}
                appliedFilters={appliedFilters}
                filterConfig={filterConfig}
            />

            <div className="px-7.5">
                <div className="pl-4 pr-2 mb-4 bg-neutral-second rounded-[10px]">
                    <SelectedFilters
                        appliedFilters={appliedFilters}
                        filterConfig={filterConfig}
                        removeFilter={removeFilter}
                        clearAllFilters={clearAllFilters}
                        searchValue={searchQuery || ''}
                        searchPlaceholder={t('search')}
                        onSearch={handleSearch}
                    />
                </div>

                {loading ? (
                    <div className="space-y-4">
                        {[...Array(3)].map((_, i) => (
                            <OutgoingMessageCardSkeleton key={i} />
                        ))}
                    </div>
                ) : messages.length === 0 ? (
                    <div className="text-sm text-secondary-third text-center py-6">
                        {t('no_outgoing_messages')}
                    </div>
                ) : (
                    <OutgoingMessageList messages={messages} />
                )}
            </div>
        </div>
    );
}
