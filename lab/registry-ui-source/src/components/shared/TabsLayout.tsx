'use client';

import { ReactNode, useEffect, useRef, useState } from "react";
import { ChevronDown } from "lucide-react";
import { BreadcrumbBar } from "@/components/shared";
import { TabsResponse } from "@/shared/types";
import { useTranslations } from "next-intl";

interface Props {
    breadcrumb: { label: string; href?: string }[];
    tabs?: TabsResponse | null;
    activeTab?: number;
    onTabChange?: (index: number) => void;
    children: ReactNode;
    rightContent?: ReactNode;
}

export default function TabsLayout({
    breadcrumb,
    tabs,
    activeTab,
    onTabChange,
    children,
    rightContent,
}: Props) {
    const t = useTranslations();
    const [isMoreOpen, setIsMoreOpen] = useState(false);
    const moreMenuRef = useRef<HTMLDivElement | null>(null);

    const MAX_VISIBLE_TABS = 5;

    const allTabs = tabs?.tabs ?? [];
    const visibleTabs = allTabs.slice(0, MAX_VISIBLE_TABS);
    const moreTabs = allTabs.slice(MAX_VISIBLE_TABS);
    const hasMoreTabs = moreTabs.length > 0;

    const isMoreActive =
        hasMoreTabs && activeTab !== undefined && activeTab >= MAX_VISIBLE_TABS;

    useEffect(() => {
        if (!isMoreOpen) return;

        const handleClickOutside = (event: MouseEvent) => {
            if (
                moreMenuRef.current &&
                !moreMenuRef.current.contains(event.target as Node)
            ) {
                setIsMoreOpen(false);
            }
        };

        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, [isMoreOpen]);

    // if activeTab change then close the dropdown of more tab
    useEffect(() => {
        setIsMoreOpen(false);
    }, [activeTab]);

    const activeMoreTab =
        hasMoreTabs &&
        activeTab !== undefined &&
        activeTab >= MAX_VISIBLE_TABS &&
        activeTab < allTabs.length
            ? allTabs[activeTab]
            : undefined;

    return (
        <div className="min-h-screen bg-secondary-first">
            <div className="px-7.5 pt-5">
                <BreadcrumbBar breadcrumb={breadcrumb} />
            </div>

            <div className="px-7.5 py-6">
                {tabs && activeTab !== undefined && onTabChange && (
                    <div className="flex flex-wrap items-center justify-between gap-4 px-10">
                        <div className="flex flex-wrap items-center gap-2">
                            {visibleTabs.map((tab, index) => {
                                const tabIndex = index;
                                const isActive = activeTab === tabIndex;

                                return (
                                    <button
                                        key={tab.tab_id}
                                        onClick={() => onTabChange(tabIndex)}
                                        className={`min-w-30 max-w-45 px-4 py-2 text-neutral-first text-[18px] font-medium rounded-t-[10px] transition-all ${
                                            isActive
                                                ? "bg-primary-first"
                                                : "bg-secondary-second"
                                        }`}
                                    >
                                        <span className="block w-full truncate text-center">
                                            {t(tab.tab_label) || tab.tab_label}
                                        </span>
                                    </button>
                                );
                            })}

                            {hasMoreTabs && (
                                <div className="relative" ref={moreMenuRef}>
                                    <button
                                        type="button"
                                        onClick={() =>
                                            setIsMoreOpen((prev) => !prev)
                                        }
                                        className={`inline-flex items-center justify-center gap-2 min-w-30 px-4 py-2 rounded-t-[10px] font-medium text-[18px] text-neutral-first transition-all whitespace-nowrap ${
                                            isMoreActive
                                                ? "bg-primary-first"
                                                : "bg-secondary-second"
                                        }`}
                                    >
                                        <span className="truncate">
                                            {activeMoreTab
                                                ? t(activeMoreTab.tab_label) ||
                                                  activeMoreTab.tab_label
                                                : t("more") || "More"}
                                        </span>
                                        <ChevronDown
                                            className={`ml-1 h-5 w-5 shrink-0 transition-transform ${
                                                isMoreOpen ? "rotate-180" : ""
                                            }`}
                                        />
                                    </button>

                                    {isMoreOpen && (
                                        <div className="origin-top-left outline-none absolute left-0 mt-0 min-w-30 rounded-b-[10px] rounded-r-[10px] bg-neutral-second border border-primary-first drop-shadow-[0_2px_6px_rgba(0,0,0,0.25)] z-50">
                                            <div className="py-1">
                                                {moreTabs.map((tab, index) => {
                                                    const tabIndex =
                                                        MAX_VISIBLE_TABS +
                                                        index;
                                                    const isActive =
                                                        activeTab === tabIndex;

                                                    return (
                                                        <button
                                                            key={tab.tab_id}
                                                            type="button"
                                                            onClick={() => {
                                                                onTabChange(
                                                                    tabIndex
                                                                );
                                                                setIsMoreOpen(
                                                                    false
                                                                );
                                                            }}
                                                            className={`block w-full max-w-62.5 text-left px-4 py-2 font-medium text-[18px] transition-colors ${
                                                                isActive
                                                                    ? "bg-primary-first/25 text-neutral-first font-semibold"
                                                                    : "text-neutral-first"
                                                            }`}
                                                        >
                                                            {t(
                                                                tab.tab_label
                                                            ) || tab.tab_label}
                                                        </button>
                                                    );
                                                })}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                        {rightContent}
                    </div>
                )}
                {children}
            </div>
        </div>
    );
}
