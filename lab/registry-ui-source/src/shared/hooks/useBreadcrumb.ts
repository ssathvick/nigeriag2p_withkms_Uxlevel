import { useMemo, useContext } from 'react';
import { useSearchParams } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { RegisterContext } from '@/context/RegisterContext';
import { RegisterTabsContext } from '@/context/RegisterTabsContext';

interface BreadcrumbItem {
    label: string;
    href: string;
}

interface BreadcrumbOptions {
    registerType?: string;
    functionalRecordId?: string | null;
    recordName?: string | null;
    internalRecordId?: string | null;
    changeId?: string;
    includeActiveTab?: boolean;
    includeChangeRequest?: boolean;
    customItems?: BreadcrumbItem[];
    rootItem?: BreadcrumbItem;
}

export function useBreadcrumb(options: BreadcrumbOptions) {
    const t = useTranslations();
    const registerCtx = useContext(RegisterContext);
    const tabsCtx = useContext(RegisterTabsContext);

    const currentRegister = registerCtx?.currentRegister;
    const activeTab = tabsCtx?.activeTab;
    const activeTabId = tabsCtx?.activeTabId;

    const searchParams = useSearchParams();
    const {
        registerType,
        functionalRecordId,
        recordName,
        internalRecordId,
        changeId,
        includeActiveTab = false,
        includeChangeRequest = false,
        customItems = [],
        rootItem,
    } = options;

    return useMemo<BreadcrumbItem[]>(() => {
        const items: BreadcrumbItem[] = [];
        const search = searchParams.toString();

        if (rootItem) {
            items.push(rootItem);
        }

        if (currentRegister && registerType) {
            items.push({
                label: t(currentRegister.register_subject) ?? currentRegister.register_subject,
                href: `/register/${registerType}${search ? `?${search}` : ''}`,
            });

            if (internalRecordId && activeTab) {
                items.push({
                    label: `${recordName} - ${functionalRecordId} - ${t(activeTab.tab_label) ?? activeTab.tab_label}`,
                    href: `/register/${registerType}/${internalRecordId}${search ? `?${search}` : ''}`,
                });
            }

            if (includeChangeRequest && internalRecordId) {
                items.push({
                    label: t('change_request') ?? 'Change Request',
                    href: `/register/${registerType}/${internalRecordId}/change-request${activeTabId ? `?tab=${activeTabId}` : ''}`,
                });
            }

            if (changeId && internalRecordId) {
                items.push({
                    label: changeId,
                    href: `/register/${registerType}/${internalRecordId}/change-request/${changeId}${activeTabId ? `?tab=${activeTabId}` : ''}`,
                });
            }
        }

        items.push(...customItems);

        return items;
    }, [
        currentRegister,
        registerType,
        functionalRecordId,
        internalRecordId,
        changeId,
        includeActiveTab,
        includeChangeRequest,
        activeTab,
        activeTabId,
        customItems,
        rootItem,
        recordName,
        t,
        searchParams,
    ]);
}
