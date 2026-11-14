'use client';

import { useCallback } from 'react';
import { useTranslations } from 'next-intl';
import { useSearchParams } from 'next/navigation';
import { useRouter } from '@/i18n/navigation';

import { TopBar } from '@/components/shared';
import { IncomingMessageCardSkeleton, IncomingMessageList } from '@/features/messages/components';
import { useIncomingMessagesList } from '@/features/messages/hooks/useIncomingMessagesList';
import { usePagination } from '@/shared/hooks';
import { useRuntimeConfig } from '@/context/RuntimeConfigContext';

export default function IncomingMessagesPage() {
    const router = useRouter();
    const t = useTranslations();
    const { config } = useRuntimeConfig();

    const searchParams = useSearchParams();
    const searchQuery = searchParams.get('search') || undefined;
    const pageSize = config.pageSize || 10;

    const {
        messages,
        loading,
        currentPage,
        paginationInfo,
        onPrev,
        onNext,
    } = useIncomingMessagesList({
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
        router.push(`/incoming-messages?${params.toString()}`);
    }, [searchParams]);

    return (
        <div className="min-h-screen mx-auto bg-secondary-first">
            <TopBar
                breadcrumb={[{ label: t('incoming_messages') }]}
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

            <div className="px-7.5">
                {loading ? (
                    <div className="space-y-4">
                        {[...Array(3)].map((_, i) => (
                            <IncomingMessageCardSkeleton key={i} />
                        ))}
                    </div>
                ) : messages.length === 0 ? (
                    <div className="text-sm text-secondary-third text-center py-6">
                        {t('no_incoming_messages')}
                    </div>
                ) : (
                    <IncomingMessageList
                        messages={messages}
                    />
                )}
            </div>
        </div>
    );
}
