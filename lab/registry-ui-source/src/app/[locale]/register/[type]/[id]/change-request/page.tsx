'use client';

import { useParams } from 'next/navigation';
import { PaginationBar, TabsLayout } from '@/components/shared';
import { ChangeRequestList, ChangeRequestSkeleton } from '@/features/change-request/components';
import { useChangeRequestList } from '@/features/change-request/hooks/useChangeRequestList';
import { useLocale, useTranslations } from 'next-intl';
import { useRegister } from '@/context/RegisterContext';
import { useRegisterTabs } from '@/context/RegisterTabsContext';
import { useBreadcrumb, usePagination } from '@/shared/hooks';
import { useRegisterRecord } from '@/context/RegisterRecordContext';
import { useRuntimeConfig } from '@/context/RuntimeConfigContext';
import { useFetch } from '@/shared/hooks/useFetch';

export default function ChangeRequestPage() {
    const t = useTranslations();
    const locale = useLocale();
    const { type: registerType, id: internalRecordId } = useParams<{ type: string; id: string }>();
    const { currentRegister } = useRegister();
    const { config } = useRuntimeConfig();

    const { functionalRecordId, recordName } = useRegisterRecord();

    const {
        tabs,
        activeTabIndex,
        activeTabId,
        setActiveTabByIndex,
    } = useRegisterTabs();

    const subjectRegisterId = currentRegister?.register_id;
    const pageSize = config.pageSize || 10;

    const {
        changeRequests,
        loading,
        currentPage,
        paginationInfo,
        onPrev,
        onNext,
    } = useChangeRequestList({
        subjectRecordId: internalRecordId,
        subjectRegisterId: subjectRegisterId,
        tabId: activeTabId,
        pageSize,
        enabled: !!activeTabId && !!internalRecordId && !!subjectRegisterId,
    });

    const { data: pendingData } = useFetch<any>({
        url: '/api/change-request/pending',
        enabled: !!subjectRegisterId && !!internalRecordId && !!activeTabId,
        options: {
            method: 'POST',
            body: JSON.stringify({
                subject_register_id: subjectRegisterId,
                subject_record_id: internalRecordId,
                tab_id: activeTabId,
            }),
        },
    });

    const { pageStart, pageEnd, total } = usePagination({
        totalItems: paginationInfo?.number_of_items ?? 0,
        currentPage,
        pageSize,
        currentCount: changeRequests.length,
    });

    const breadcrumb = useBreadcrumb({
        registerType,
        functionalRecordId,
        recordName,
        internalRecordId,
        includeActiveTab: true,
        includeChangeRequest: true,
    });

    // Right side of TabsLayout-- Pending request + pagination
    const pendingRequestsCount = pendingData?.number_of_pending_change_requests ?? 0;
    const rightContent = !loading && (
        <div className="flex items-center gap-10">
            {pendingRequestsCount !== undefined && (
                <div className="flex items-center gap-2">
                    <span className="text-[18px] font-medium text-neutral-first">
                        {t('pending_requests')}
                    </span>
                    <span className="text-[24px] font-bold text-primary-second">
                        {pendingRequestsCount.toString().padStart(2, '0')}
                    </span>
                </div>
            )}
            <div className='mb-2.5'>
                <PaginationBar
                    pageStart={pageStart ?? 0}
                    pageEnd={pageEnd ?? 0}
                    total={total ?? 0}
                    onPrev={onPrev}
                    onNext={onNext}
                />
            </div>
        </div>
    );

    return (
        <TabsLayout
            breadcrumb={breadcrumb}
            tabs={{ tabs }}
            activeTab={activeTabIndex}
            onTabChange={setActiveTabByIndex}
            rightContent={rightContent}
        >
            {loading ? (
                <>
                    {(tabs.length === 0 && <div className="flex gap-2 px-10">
                        {[1, 2, 3].map(i => (
                            <div
                                key={i}
                                className="h-11 w-32 rounded-t-[10px] bg-primary-first/50"
                            />
                        ))}
                    </div>)}
                    <div className="space-y-4">
                        {[...Array(3)].map((_, i) => (
                            <ChangeRequestSkeleton key={i} />
                        ))}
                    </div>
                </>
            ) : changeRequests.length === 0 ? (
                <div className="px-6 py-5 flex items-center justify-center text-center">
                    <div className="text-[16px] text-neutral-first/50 font-medium">
                        {t("no_change_request")}
                    </div>
                </div>
            ) : (
                <>
                    <ChangeRequestList
                        changeRequests={changeRequests}
                        getDetailsUrl={changeRequest =>
                            `/${locale}/register/${registerType}/${internalRecordId}/change-request/${changeRequest.change_request_id}?tab=${activeTabId}`
                        }
                    />
                </>
            )}
        </TabsLayout>
    );
}
