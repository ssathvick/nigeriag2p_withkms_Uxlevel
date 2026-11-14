import { useMemo } from "react";
import { useParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { useBreadcrumb } from "@/shared/hooks";
import { useRegister } from "@/context/RegisterContext";
import { useRegisterTabs } from "@/context/RegisterTabsContext";
import { useRegisterRecord } from "@/context/RegisterRecordContext";
import { createWidgetStore } from "@openg2p/registry-widgets";
import { useRegisterSections } from "./useRegisterSections";

export const useRegisterDetail = (onChangeRequestCreated: () => void) => {
    const t = useTranslations();
    const { type: registerType } = useParams<{ type: string }>();
    const {
        internalRecordId,
        functionalRecordId,
        recordName,
        loading: resolvingId,
    } = useRegisterRecord();

    const widgetStore = useMemo(() => createWidgetStore(), []);

    const { tabs, activeTabIndex, activeTabId, setActiveTabByIndex } = useRegisterTabs();

    const { currentRegister } = useRegister();

    const breadcrumb = useBreadcrumb({
        registerType,
        functionalRecordId,
        recordName,
        internalRecordId,
        includeActiveTab: true,
    });

    const {
        tabSections,
        orderedTabSections,
        sectionDataMap,
        handleSectionSave,
        canRenderContent,
    } = useRegisterSections(onChangeRequestCreated);

    return {
        registerType,
        t,
        internalRecordId,
        resolvingId,
        widgetStore,
        tabs,
        activeTabIndex,
        setActiveTabByIndex,
        activeTabId,
        breadcrumb,
        tabSections,
        orderedTabSections,
        sectionDataMap,
        handleSectionSave,
        canRenderContent,
        currentRegister,
    };
};
