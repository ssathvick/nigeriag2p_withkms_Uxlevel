'use client';

import { useTranslations } from 'next-intl';
import {
    TabsLayout,
} from '@/components/shared';
import {
    WidgetProvider,
    SectionRenderer,
} from '@openg2p/registry-widgets';
import RegisterChangeRequestCard from '@/features/change-request/components/RegisterChangeRequestCard';
import { useState } from 'react';

import { useRegisterDetail } from '@/features/register/hooks/useRegisterDetail';
import RegisterDetailsPageSkeleton from '@/features/register/components/RegisterDetailsPageSkeleton';
import { dataSourceRequestHandler } from '@/features/register/utils/dataSourceRequestHandler';
import { VersionHistoryCard } from '@/features/register/components';


export default function RegisterDetailPage() {
    const t = useTranslations();

    // state to update the count of pending change requests
    const [changeRequestCount, setChangeRequestCount] = useState<number | undefined>(undefined);

    const {
        internalRecordId,
        registerType,
        widgetStore,
        tabs,
        activeTabIndex,
        setActiveTabByIndex,
        activeTabId,
        breadcrumb,
        orderedTabSections,
        sectionDataMap,
        handleSectionSave,
        canRenderContent,
        currentRegister
    } = useRegisterDetail(() => setChangeRequestCount(prevCount => (prevCount ?? 0) + 1));

    const isLoading = !internalRecordId || !canRenderContent;
    const isNotFound = !internalRecordId;

    return (
        <TabsLayout
            breadcrumb={breadcrumb}
            tabs={{ tabs }}
            activeTab={activeTabIndex}
            onTabChange={setActiveTabByIndex}
        >
            {isLoading ? (
                <RegisterDetailsPageSkeleton tabs={tabs} />
            ) : isNotFound ? (
                <div className="p-8 text-center text-toast-failed bg-neutral-second rounded-lg border border-red-100 shadow-sm">
                    {t('record_not_found')}
                </div>
            ) : (
                <div className="grid grid-cols-12 gap-6">
                    <div className="col-span-12 lg:col-span-9">
                        <div className="col-span-12 lg:col-span-9">
                            {orderedTabSections.length > 0 && sectionDataMap ? (
                                <WidgetProvider
                                    key={activeTabId}
                                    store={widgetStore}
                                    schemaData={sectionDataMap}
                                    translate={t}
                                    dataSourceRequestHandler={dataSourceRequestHandler}
                                >
                                    {orderedTabSections.map((section) => {
                                        const { section_id, section_register_id, section_ui_schema, hideEditButton } = section;

                                        return (
                                            <div key={section_id} className='pb-4'>
                                                <SectionRenderer
                                                    section={section_ui_schema}
                                                    onSectionSave={handleSectionSave}
                                                    hideEditButton={hideEditButton}
                                                    dataSourceRequestHandler={dataSourceRequestHandler}
                                                    dbSectionId={section_id}
                                                    sectionRegisterId={section_register_id}
                                                />
                                            </div>
                                        );
                                    })}
                                </WidgetProvider>
                            ) : !isLoading && (
                                <div className=" px-6 py-5 flex items-center justify-center text-center">
                                    <div className="text-[16px] text-neutral-first/50 font-medium">
                                        {t("no_tab_section")}
                                    </div>
                                </div>
                            )}

                        </div>
                    </div>

                    <div className="col-span-12 lg:col-span-3 flex flex-col gap-6">
                        {currentRegister && internalRecordId && (
                            <>
                                <RegisterChangeRequestCard
                                    type={registerType}
                                    registerId={currentRegister.register_id}
                                    internalRecordId={internalRecordId}
                                    activeTabId={activeTabId}
                                    count={changeRequestCount}
                                    onCountLoaded={setChangeRequestCount}
                                />
                                <VersionHistoryCard
                                    type={registerType}
                                    registerId={currentRegister.register_id}
                                    internalRecordId={internalRecordId}
                                    activeTabId={activeTabId}
                                />
                            </>
                        )}
                    </div>
                </div>
            )}
        </TabsLayout>
    );
}
