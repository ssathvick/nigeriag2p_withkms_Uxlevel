'use client';

import { useState } from 'react';
import { TopBar } from '@/components/shared';
import { useAllSubscriptionActivityLogs, useSubscriptionActivityLog } from '@/features/configuration/shared';
import { usePagination } from '@/shared/hooks';
import { useRuntimeConfig } from '@/context/RuntimeConfigContext';
import { useTranslations } from 'next-intl';
import { SubscriptionActivityLog } from '@/features/configuration/shared/hooks/useAllSubscriptionActivityLogs';
import { useRbac } from '@/context/RbacContext';
import { CONFIGURATION_SUBSCRIPTION_ACTIONS } from '@/features/configuration/shared/utils/configurationSubscription.actions';
import AddSubscriptionActivityLogModal from '@/features/configuration/ingest/AddSubscriptionActivityLogModal';
import ViewSubscriptionActivityLogModal from '@/features/configuration/ingest/ViewSubscriptionActivityLogModal';
import { DataTable, ViewButton } from '@/features/configuration/shared/components';

const ManageSubscriptionPage = () => {
    const t = useTranslations();
    const [modalType, setModalType] = useState<'add' | 'view' | null>(null);
    const [currentPage, setCurrentPage] = useState(1);
    const { config } = useRuntimeConfig();
    const { can } = useRbac();

    const { activityLogs, pagination, loading, refresh } = useAllSubscriptionActivityLogs(currentPage, config.pageSize);
    const { selectedActivityLog, fetchActivityLog } = useSubscriptionActivityLog();

    const { pageStart, pageEnd, total } = usePagination({
        totalItems: pagination?.number_of_items || 0,
        currentPage: currentPage,
        pageSize: config?.pageSize || 10,
        currentCount: activityLogs.length,
    });

    const handlePrev = () => {
        setCurrentPage((prev) => Math.max(1, prev - 1));
    };

    const handleNext = () => {
        setCurrentPage((prev) => prev + 1);
    };

    const handleView = async (log: SubscriptionActivityLog) => {
        const result = await fetchActivityLog(log.subscription_activity_log_id);
        if (result) {
            setModalType('view');
        }
    };

    const columns = [
        {
            key: 'subscription_activity_log_id',
            label: t('activity_log_id'),
        },
        {
            key: 'partner_id',
            label: t('partner_id'),
        },
        {
            key: 'unsubscribe',
            label: t('unsubscribe'),
            render: (item: SubscriptionActivityLog) => item.is_unsubscribe ? t('true') : t('false'),
        },
        {
            key: 'date_time',
            label: t('date_time'),
            render: (item: SubscriptionActivityLog) => new Date(item.date_time).toLocaleString(),
        },
    ];

    return (
        <>
            <TopBar
                breadcrumb={[{ label: t('ingest_configurations') }, { label: t('subscription_logs') }]}
                showFilters={false}
                showPagination
                showAddNewButton={can(CONFIGURATION_SUBSCRIPTION_ACTIONS.create)}
                addNewButtonText={t('add_subscription_log')}
                onAddNewButton={() => setModalType('add')}
                pageStart={pageStart}
                pageEnd={pageEnd}
                total={total}
                onPrev={handlePrev}
                onNext={handleNext}
            />

            <DataTable
                columns={columns}
                data={activityLogs}
                loading={loading}
                rowKey={(item) => item.subscription_activity_log_id}
                actions={(item) => (
                    <ViewButton
                        label={t('view')}
                        onClick={() => handleView(item)}
                    />
                )}
            />

            {modalType === 'add' && (
                <AddSubscriptionActivityLogModal
                    onClose={() => setModalType(null)}
                    onSuccess={refresh}
                />
            )}

            {modalType === 'view' && (
                <ViewSubscriptionActivityLogModal
                    onClose={() => setModalType(null)}
                    data={selectedActivityLog}
                />
            )}
        </>
    );
};

export default ManageSubscriptionPage;
