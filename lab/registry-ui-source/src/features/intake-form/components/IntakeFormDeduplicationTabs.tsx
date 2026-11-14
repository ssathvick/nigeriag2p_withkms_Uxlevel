"use client";
import {InfoHint} from '@/components/shared/Workflow';

interface Props {
  activeTab: "intake_forms" | "intake_possible_duplicates" | "register_possible_duplicates";
  setActiveTab: (tab: "intake_forms" | "intake_possible_duplicates" | "register_possible_duplicates") => void;
  intakeResultsCount: number;
  regResultsCount: number;
  t: (key: string) => string;
}

export default function IntakeFormDeduplicationTabs({
  activeTab,
  setActiveTab,
  intakeResultsCount,
  regResultsCount,
  t,
}: Props) {
  return (
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
        Intake Duplicates<InfoHint text="Possible matches in other intake submissions awaiting registration. Compare their details before deciding."/>
        {intakeResultsCount > 0 && (
          <span className="absolute -top-3 right-3 bg-toast-failed text-neutral-second text-[12px] font-bold rounded-[10px] w-6 h-6 flex items-center justify-center shadow-sm">
            {String(intakeResultsCount).padStart(2, "0")}
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
        Existing Duplicates<InfoHint text="Possible matches in the approved master registry. Compare the existing household or individual before deciding."/>
        {regResultsCount > 0 && (
          <span className="absolute -top-3 right-3 bg-toast-failed text-neutral-second text-[12px] font-bold rounded-[10px] w-6 h-6 flex items-center justify-center shadow-sm">
            {String(regResultsCount).padStart(2, "0")}
          </span>
        )}
      </button>
    </div>
  );
}
