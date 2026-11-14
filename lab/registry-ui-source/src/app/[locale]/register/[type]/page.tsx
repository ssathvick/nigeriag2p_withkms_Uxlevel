'use client';

import { useTranslations } from 'next-intl';
import { TopBar } from '@/components/shared';
import { SelectedFilters } from '@/features/filter/components';
import { useRegisterRecords } from '@/features/register/hooks/useRegisterRecords';
import { RegisterRecordCard } from '@/features/register/components';
import { RegisterRecord } from '@/features/register/types';

export default function RegisterTypePage() {
    const t = useTranslations();

    const {
        registerType,
        registerTypeLabel,
        records,
        isLoadingRecords,
        searchQuery,
        pagination,
        handlers: {
            handlePreviousPage,
            handleNextPage,
            handleSearch
        },
        filters: {
            appliedFilters,
            filterConfig,
            applyFilters,
            removeFilter,
            clearAllFilters
        }
    } = useRegisterRecords();

    return (
        <div className="min-h-screen mx-auto bg-secondary-first">
            <TopBar
                breadcrumb={[{ label: registerTypeLabel }]}
                showFilters
                showPagination
                showCapsule={false}
                capsule={<></>}
                pageStart={pagination.pageStart}
                pageEnd={pagination.pageEnd}
                total={pagination.total}
                onPrev={handlePreviousPage}
                onNext={handleNextPage}
                onApplyFilters={applyFilters}
                appliedFilters={appliedFilters}
                filterConfig={filterConfig}
            />

            <div className="mx-7.5 bg-neutral-second rounded-[10px]">
                <div className="px-2 pt-1">
                    <SelectedFilters
                        appliedFilters={appliedFilters}
                        filterConfig={filterConfig}
                        removeFilter={removeFilter}
                        clearAllFilters={clearAllFilters}
                        searchValue={searchQuery}
                        searchPlaceholder={t('search')}
                        onSearch={handleSearch}
                        pxClass='px-0.5'
                    />
                </div>

                <div className="rounded-b-[10px]">
                    {isLoadingRecords ? (
                        <div className="space-y-2">
                            {[...Array(5)].map((_, i) => (
                                <div
                                    key={i}
                                    className="flex items-center gap-4 sm:gap-6 px-4 sm:px-6 lg:px-8 p-4 w-full overflow-hidden bg-secondary-second animate-pulse"
                                >
                                    <div className="w-16 h-16 rounded-md bg-secondary-third shrink-0" />
                                    <div className="flex-1 space-y-2 min-w-0">
                                        <div className="h-4 bg-secondary-third rounded w-1/3" />
                                        <div className="h-3 bg-secondary-third rounded w-1/2" />
                                    </div>
                                    <div className="flex-1 space-y-2 min-w-0">
                                        <div className="h-3 bg-secondary-third rounded w-2/3" />
                                        <div className="h-3 bg-secondary-third rounded w-1/2" />
                                    </div>
                                    <div className="flex-1 space-y-2 min-w-0">
                                        <div className="h-3 bg-secondary-third rounded w-1/3" />
                                        <div className="h-3 bg-secondary-third rounded w-2/3" />
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : records.length === 0 ? (
                        <div className="text-center py-10 text-neutral-first/50">{t('no_items_found')}</div>
                    ) : (
                        records.map((record: RegisterRecord, index: number) => (
                            <RegisterRecordCard
                                key={record.internal_record_id}
                                record={record}
                                registerType={registerType}
                                isEven={index % 2 === 0}
                            />
                        ))
                    )}
                    <div className={`h-6.25 rounded-b-[10px] ${records.length % 2 !== 0 ? 'bg-neutral-second' : 'bg-secondary-second/25'}`}>
                        &nbsp;
                    </div>
                </div>
            </div>
            <div className='h-15'>&nbsp;</div>
        </div>
    );
}
