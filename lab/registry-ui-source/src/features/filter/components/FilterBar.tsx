"use client";

import Image from "next/image";
import { useRef, useState } from "react";
import FilterDropdown from "./FilterDropdown";
import { useClickOutside } from "@/shared/hooks/useClickOutside";
import { FilterConfig, FilterRule } from "@/features/filter/types";
import { useTranslations } from 'next-intl';

interface FilterBarProps {
    onFilters?: () => void;
    onApplyFilters?: (filters: FilterRule[]) => void;
    appliedFilters?: FilterRule[];
    filterConfig?: FilterConfig[];
    filterLoading?: boolean;
}

export default function FilterBar({
    onFilters,
    onApplyFilters,
    appliedFilters = [],
    filterConfig = [],
    filterLoading = false
}: FilterBarProps) {
    const t = useTranslations();
    const [open, setOpen] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);

    useClickOutside(dropdownRef, () => setOpen(false), open);

    const handleApply = (filters: FilterRule[]) => {
        setOpen(false);
        if (onFilters) onFilters();
        if (onApplyFilters) onApplyFilters(filters);
    };

    if(!filterLoading&&!filterConfig.length)return null;
    return (
        <div className="relative inline-block items-center" onKeyDown={e=>{if(e.key==="Escape")setOpen(false)}} ref={dropdownRef}>
            <button
                aria-label="Filters" aria-expanded={open} aria-haspopup="dialog" aria-busy={filterLoading} onClick={() => setOpen((prev) => !prev)}
                className="w-[130px] h-[34px] flex items-center justify-between px-4 rounded-[10px] bg-primary-first"
                disabled={filterLoading}
            >   <span className=" text-[16px] font-medium leading-normal text-neutral-first">
                    {filterLoading ? t('filter_loading') : t('filters')}
                </span>

                <Image src="/images/common/filters_icon.png" width={24} height={24} alt={t('filters')} />
            </button>

            {open && !filterLoading && (
                <div className="application-filter-popover absolute right-0 top-12 z-50">
                    <div
                        className="absolute -top-[9px] right-[45px] z-20 bg-neutral-second border-t border-r border-primary-first w-[20px] h-[20px] -rotate-45 rounded-[2px] shadow-[0_0_4px_0_rgba(0,0,0,0.25)] [clip-path:polygon(-20px_-20px,_40px_-20px,_40px_40px)]"
                    />
                    <div className="relative z-10">
                        <FilterDropdown
                            onApply={handleApply}
                            onClose={() => setOpen(false)}
                            appliedFilters={appliedFilters}
                            filterConfig={filterConfig}
                        />
                    </div>
                </div>
            )}
        </div>
    );
}
