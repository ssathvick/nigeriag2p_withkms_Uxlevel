"use client";

import { useState } from "react";
import {
    WidgetProvider,
    SectionRenderer,
} from "@openg2p/registry-widgets";
import { dataSourceRequestHandler } from "@/features/register/utils/dataSourceRequestHandler";
import { useDeduplication } from "@/features/change-request/hooks";
import DeduplicationCard from "./DeduplicationCard";

type TabType = "change_request_values" | "cr_possible_duplicates" | "register_possible_duplicates";

export function ChangeRequestValuesTabs({
    widgetStoreNew,
    widgetStoreOld,
    newSectionData,
    oldSectionData,
    sectionUISchema,
    t,
    changeId,
}: any) {
    const [activeTab, setActiveTab] = useState<TabType>("change_request_values");

    const { results: crResults, loading: crLoading } = useDeduplication(changeId, "change-request");
    const { results: regResults, loading: regLoading } = useDeduplication(changeId, "register");

    return (
        <div className="mt-7.5">
            <div className="ml-7.5">
                <button
                    onClick={() => setActiveTab("change_request_values")}
                    className={`px-8 py-2 text-neutral-first text-[18px] font-medium rounded-t-[10px] transition-all ${activeTab === "change_request_values"
                        ? 'bg-primary-first'
                        : 'bg-secondary-second'
                        }`}
                >
                    {t("new_and_old_values")}
                </button>

                <button
                    onClick={() => setActiveTab("cr_possible_duplicates")}
                    className={`relative ml-2 px-8 py-2 text-neutral-first text-[18px] font-medium rounded-t-[10px]
                        ${activeTab === "cr_possible_duplicates"
                            ? "bg-primary-first"
                            : "bg-secondary-second"
                        }`}
                >
                    {t("cr_possible_duplicates")}
                    {crResults.length > 0 && (
                        <span className="absolute -top-3 right-3 bg-toast-failed text-neutral-second text-[12px] font-bold rounded-[10px] w-6 h-6 flex items-center justify-center shadow-sm">
                            {String(crResults.length).padStart(2, "0")}
                        </span>
                    )}
                </button>

                <button
                    onClick={() => setActiveTab("register_possible_duplicates")}
                    className={`relative ml-2 px-8 py-2 text-neutral-first text-[18px] font-medium rounded-t-[10px]
                        ${activeTab === "register_possible_duplicates"
                            ? "bg-primary-first"
                            : "bg-secondary-second"
                        }`}
                >
                    {t("register_possible_duplicates")}
                    {regResults.length > 0 && (
                        <span className="absolute -top-3 right-3 bg-toast-failed text-neutral-second text-[12px] font-bold rounded-[10px] w-6 h-6 flex items-center justify-center shadow-sm">
                            {String(regResults.length).padStart(2, "0")}
                        </span>
                    )}
                </button>
            </div>

            {activeTab === "change_request_values" && newSectionData && sectionUISchema && (
                <div className="flex flex-col gap-4">
                    <WidgetProvider
                        store={widgetStoreNew}
                        schemaData={newSectionData}
                        translate={t}
                        dataSourceRequestHandler={dataSourceRequestHandler}
                    >
                        <SectionRenderer
                            section={sectionUISchema}
                            hideEditButton={true}
                            mode="CRView"
                            changeRequestType="new"
                        />
                    </WidgetProvider>

                    <WidgetProvider
                        store={widgetStoreOld}
                        schemaData={oldSectionData}
                        translate={t}
                        dataSourceRequestHandler={dataSourceRequestHandler}
                    >
                        <SectionRenderer
                            section={sectionUISchema}
                            hideEditButton={true}
                            mode="CRView"
                            changeRequestType="old"
                        />
                    </WidgetProvider>
                </div>
            )}

            {activeTab === "cr_possible_duplicates" && (
                <DeduplicationCard results={crResults} loading={crLoading} type="change-request" t={t} />
            )}

            {activeTab === "register_possible_duplicates" && (
                <DeduplicationCard results={regResults} loading={regLoading} type="register" t={t} />
            )}
        </div>
    );
}
