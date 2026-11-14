"use client";

import { useState } from "react";
import DeduplicationCardForIntake from "./DeduplicationCardForIntake";
import { useIntakeDeduplication } from "../hooks/useIntakeDeduplication";

type TabType = "intake_forms" | "intake_possible_duplicates" | "register_possible_duplicates";

export function IntakeFormValuesTabs({
    submissionId,
    t,
    children
}: any) {
    const [activeTab, setActiveTab] = useState<TabType>("intake_forms");

    const { results: intakeResults, loading: intakeLoading } = useIntakeDeduplication(submissionId, "intake-form");
    const { results: regResults, loading: regLoading } = useIntakeDeduplication(submissionId, "register");

    return (
        <div className="mt-7.5">
            <div className="ml-7.5">
                <button
                    onClick={() => setActiveTab("intake_forms")}
                    className={`px-8 py-2 text-neutral-first text-[18px] font-medium rounded-t-[10px] transition-all ${activeTab === "intake_forms"
                        ? 'bg-primary-first'
                        : 'bg-secondary-second'
                        }`}
                >
                    {t("intake_forms")}
                </button>

                <button
                    onClick={() => setActiveTab("intake_possible_duplicates")}
                    className={`relative ml-2 px-8 py-2 text-neutral-first text-[18px] font-medium rounded-t-[10px]
                        ${activeTab === "intake_possible_duplicates"
                            ? "bg-primary-first"
                            : "bg-secondary-second"
                        }`}
                >
                    {t("intake_possible_duplicates")}
                    {intakeResults.length > 0 && (
                        <span className="absolute -top-3 right-3 bg-toast-failed text-neutral-second text-[12px] font-bold rounded-[10px] w-6 h-6 flex items-center justify-center shadow-sm">
                            {String(intakeResults.length).padStart(2, "0")}
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

            {activeTab === "intake_forms" && (
                <div className="flex flex-col gap-4">
                    {children}
                </div>
            )}

            {activeTab === "intake_possible_duplicates" && (
                <DeduplicationCardForIntake results={intakeResults} loading={intakeLoading} type="intake-form" t={t} />
            )}

            {activeTab === "register_possible_duplicates" && (
                <DeduplicationCardForIntake results={regResults} loading={regLoading} type="register" t={t} />
            )}
        </div>
    );
}
