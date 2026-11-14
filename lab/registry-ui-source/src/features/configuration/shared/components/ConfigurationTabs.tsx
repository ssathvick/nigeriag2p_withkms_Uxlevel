'use client';

import { useState, useRef } from 'react';
import { ChevronDown } from 'lucide-react';
import { useClickOutside } from '@/shared/hooks';
import { useTranslations } from 'next-intl';

interface ConfigurationTabsProps {
    activeTab: string;
    setActiveTab: (tab: any) => void;
    tabLabels: Record<string, string>;
}

const MAX_VISIBLE_TABS = 2;

const TabsDropdown = ({
    options,
    activeTab,
    onTabChange,
    labelMap,
    isMore = false
}: {
    options: string[],
    activeTab: string,
    onTabChange: (tab: any) => void,
    labelMap: Record<string, string>,
    isMore?: boolean
}) => {
    const [isOpen, setIsOpen] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);
    const isActiveInDropdown = options.includes(activeTab);
    const t = useTranslations();

    useClickOutside(dropdownRef, () => setIsOpen(false), isOpen);

    return (
        <div className="relative inline-block text-center " ref={dropdownRef}>
            <div>
                <button
                    type="button"
                    onClick={() => setIsOpen(!isOpen)}
                    className={`inline-flex justify-center items-center min-w-30 px-4 py-2 rounded-t-[10px] font-medium text-[18px]
             ${isActiveInDropdown ? 'bg-primary-first text-neutral-first' : 'bg-secondary-second text-neutral-first '
                        }`}
                >
                    <span className="truncate">
                        {isActiveInDropdown ? labelMap[activeTab] : (isMore ? (t('more') || 'More') : labelMap[activeTab])}
                    </span>
                    <ChevronDown className={`ml-2 h-6 w-6 shrink-0 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
                </button>
            </div>

            {isOpen && (
                <div className="origin-top-left outline-none absolute left-0 mt-0 min-w-30
                rounded-b-[10px] rounded-r-[10px] bg-neutral-second border border-primary-first drop-shadow-[0_2px_6px_rgba(0,0,0,0.25)]
                z-50
                ">
                    <div className="py-1">
                        {options.map((option) => (
                            <button
                                key={option}
                                onClick={() => {
                                    onTabChange(option);
                                    setIsOpen(false);
                                }}
                                className={` block w-full max-w-62.5 text-left px-4 py-2 font-medium text-[18px] transition-colors ${activeTab === option
                                    ? 'bg-primary-first/25 text-neutral-first font-semibold'
                                    : 'text-neutral-first'
                                    }`}
                            >
                                {labelMap[option]}
                            </button>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default function ConfigurationTabs({
    activeTab,
    setActiveTab,
    tabLabels
}: ConfigurationTabsProps) {
    const tabKeys = Object.keys(tabLabels);
    const inlineTabs = tabKeys.slice(0, MAX_VISIBLE_TABS);
    const moreTabs = tabKeys.slice(MAX_VISIBLE_TABS);

    return (
        <div className="flex gap-2 items-end h-full">
            {inlineTabs.map((key) => (
                <button
                    key={key}
                    onClick={() => setActiveTab(key as any)}
                    className={`min-w-30 max-w-45 px-4 py-2 rounded-t-[10px] font-medium text-[18px]
      ${activeTab === key
                            ? 'bg-primary-first text-neutral-first'
                            : 'bg-secondary-second text-neutral-first'
                        }`}
                >
                    <span className="block w-full truncate text-center">
                        {tabLabels[key]}
                    </span>
                </button>
            ))}

            {moreTabs.length > 0 && (
                <TabsDropdown
                    options={moreTabs}
                    activeTab={activeTab}
                    onTabChange={setActiveTab}
                    labelMap={tabLabels}
                    isMore
                />
            )}
        </div>
    );
}
