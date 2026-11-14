'use client';

import { useState } from 'react';
import { TopBar, BreadcrumbBar } from '@/components/shared';
import { useParams } from 'next/navigation';
import {
    EditTabModal,
    RegisterTabSectionConfigView,
} from '@/features/configuration/registers';
import {
    ConfigDetailsSummary,
    useAllRegister,
    useConfigTabs,
    getRegisterDetails,
    getTabDetails
} from '@/features/configuration/shared';
import { useBreadcrumb } from '@/shared/hooks/useBreadcrumb';
import { usePagination } from '@/shared/hooks/usePagination';
import { useRuntimeConfig } from '@/context/RuntimeConfigContext';
import { useRbac } from '@/context/RbacContext';
import { CONFIGURATION_TABS_ACTIONS } from '@/features/configuration/shared/utils/configurationTabs.actions';
import { CONFIGURATION_SECTIONS_ACTIONS } from '@/features/configuration/shared/utils/configurationSections.actions';
import { useTranslations } from 'next-intl';

const TabConfigurationPage = () => {
    const t = useTranslations();
    const { registerId, tabId } = useParams<{ registerId: string; tabId: string }>();
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isEditTabModalOpen, setIsEditTabModalOpen] = useState(false);
    const [currentPage, setCurrentPage] = useState(1);
    const { config } = useRuntimeConfig();
    const PAGE_SIZE = config.pageSize || 10;
    const [paginationInfo, setPaginationInfo] = useState({ totalItems: 0, currentCount: 0 });

    const { can } = useRbac();
    const canEdit = can(CONFIGURATION_TABS_ACTIONS.edit);
    const canCreate = can(CONFIGURATION_SECTIONS_ACTIONS.create);

    const { registers, loading: registersLoading } = useAllRegister(1, 100);
    const { tabs, loading: tabsLoading, refresh: refreshTabs } = useConfigTabs(registerId, 1, 100);

    const pagination = usePagination({
        currentPage,
        pageSize: PAGE_SIZE,
        totalItems: paginationInfo.totalItems,
        currentCount: paginationInfo.currentCount,
    });

    const registerDetails = getRegisterDetails(registerId, registers);
    const tabDetails = getTabDetails(tabId, tabs);

    const rawLabel = tabDetails.tab_label || '';
    const label_name = rawLabel.charAt(0).toUpperCase() + rawLabel.slice(1);

    const breadcrumb = useBreadcrumb({
        rootItem: { label: t('registers'), href: '/configuration/registers' },
        customItems: [
            { label: registerDetails.register_mnemonic || '', href: `/configuration/registers/${registerId}` },
            { label: label_name || '', href: `/configuration/registers/${registerId}/tabs/${tabId}` }
        ]
    });

    const handlePrev = () => {
        setCurrentPage(prev => Math.max(1, prev - 1));
    };

    const handleNext = () => {
        setCurrentPage(prev => prev + 1);
    };

    if (registersLoading || tabsLoading) {
        return (
            <div className="flex items-center justify-center p-20">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-second"></div>
            </div>
        );
    }




    return (
        <>
            <div className="pt-10 px-7.5 mb-6">
                <BreadcrumbBar breadcrumb={breadcrumb} />
            </div>

            <ConfigDetailsSummary
                title={label_name || "None"}
                extraInfo1={registerDetails.register_mnemonic || 'None'}
                extraInfo2={String(tabDetails.tab_order ?? 0)}
                onEdit={
                    canEdit
                        ? () => setIsEditTabModalOpen(true)
                        : undefined
                }
            />

            <TopBar
                breadcrumb={[]}
                showFilters={false}
                showPagination={true}
                showSubHeading
                subHeading={`${label_name} ${t('sections')}`}
                showAddNewButton={canCreate}
                addNewButtonText={t('add_new_section')}
                onAddNewButton={() => setIsModalOpen(true)}
                pageStart={pagination.pageStart}
                pageEnd={pagination.pageEnd}
                total={pagination.total}
                onPrev={handlePrev}
                onNext={handleNext}
            />

            <RegisterTabSectionConfigView
                isModalOpen={isModalOpen}
                onCloseModal={() => setIsModalOpen(false)}
                page={currentPage}
                pageSize={PAGE_SIZE}
                onDataLoaded={(totalItems, currentCount) => setPaginationInfo({ totalItems, currentCount })}
            />

            {isEditTabModalOpen && (
                <EditTabModal
                    initialData={tabDetails as any}
                    registerId={registerId}
                    onClose={() => setIsEditTabModalOpen(false)}
                    onSuccess={refreshTabs}
                />
            )}
        </>
    );
};


export default TabConfigurationPage;
