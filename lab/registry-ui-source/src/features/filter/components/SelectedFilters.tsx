"use client";
import {readableLabel} from '@/shared/utils/readableLabel';

import Image from "next/image";
import { FilterConfig, FilterRule } from "@/features/filter/types";
import { SearchBar } from "@/components/ui";
import { useTranslations } from "next-intl";

const OPERATOR_KEYS: Record<string, string> = {
    eq: "filter_operator_eq",
    neq: "filter_operator_neq",
    in: "filter_operator_in",
    nin: "filter_operator_nin",
    contains: "filter_operator_contains",
    ncontains: "filter_operator_ncontains",
    startsWith: "filter_operator_startsWith",
    endsWith: "filter_operator_endsWith",
    gt: "filter_operator_gt",
    gte: "filter_operator_gte",
    lt: "filter_operator_lt",
    lte: "filter_operator_lte",
    isNull: "filter_operator_isNull",
    between: "filter_operator_between",
};

interface SelectedFiltersProps {
    appliedFilters: FilterRule[];
    filterConfig: FilterConfig[];
    removeFilter: (index: number) => void;
    clearAllFilters: () => void;
    searchValue?: string;
    searchPlaceholder?: string;
    onSearch?: (value: string) => void;
    pxClass?: string;
}

export default function SelectedFilters({
    appliedFilters,
    filterConfig,
    removeFilter,
    clearAllFilters,
    searchValue = '',
    searchPlaceholder,
    onSearch,
    pxClass
}: SelectedFiltersProps) {
    const t = useTranslations();
    const label=(key:string)=>t.has(key)?t(key):readableLabel(key);
    const resolvedSearchPlaceholder = searchPlaceholder || t('search');

    const getFilterLabel = (rule: FilterRule) => {
        const config = filterConfig.find((f) => f.field_name === rule.field_name);
        let valueLabel = rule.value;
        if (Array.isArray(rule.value)) {
            valueLabel = rule.value.join(' - ');
        } else if (config?.filter_type === 'dropdown' && config.options_source) {
            const option = config.options_source.find((o) => o.value === rule.value);
            valueLabel = option?.label || rule.value;
        } else if (config?.filter_type === 'boolean' && typeof rule.value === 'boolean') {
            valueLabel = rule.value ? t('true') : t('false');
        }

        return `${label(config?.display_label || rule.field_name)}: ${t(OPERATOR_KEYS[rule.operator] ?? rule.operator)} ${valueLabel || ''}`;
    };

    return (
        <div className="application-selected-filters bg-neutral-second px-4 py-4 mb-2 flex items-center rounded-[10px] gap-4">
            <div className="flex flex-wrap items-center gap-4 flex-1">
                <span className="w-27.5 font-normal text-[16px] text-neutral-first pl-1 truncate" title={t('selected_filters')}>
                    {t('selected_filters')}
                </span>

                {appliedFilters.length === 0 ? (
                    <div className="h-8.5 flex items-center bg-primary-first/25 rounded-[10px] px-3 text-neutral-first/50 font-['Roboto'] text-[14px] not-italic font-normal leading-normal">
                        {t('none')}
                    </div>
                ) : (
                    appliedFilters.map((filter, index) => (
                        <div
                            key={index}
                            className="application-filter-chip h-8.5 flex items-center bg-primary-first/25 rounded-[10px] px-3 gap-2 text-neutral-first/50 text-[14px] font-normal leading-normal"
                        >
                            <span>{getFilterLabel(filter)}</span>
                            <button
                                onClick={() => removeFilter(index)}
                                aria-label={t('remove')}
                            >
                                <Image src="/images/common/close.png" width={16} height={16} alt={t('common.remove')} />
                            </button>
                        </div>
                    ))
                )}

                {appliedFilters.length > 0 && (
                    <button
                        onClick={clearAllFilters}
                        className="text-primary-second text-sm"
                    >
                        {t('clear_all')}
                    </button>
                )}
            </div>

            {onSearch && (
                <div className="ml-auto shrink-0 border border-primary-second rounded-[10px] h-8.5 flex items-center bg-neutral-second">
                    <SearchBar
                        placeholder={resolvedSearchPlaceholder}
                        category=""
                        searchValue={searchValue}
                        iconSize={16}
                        onSearch={onSearch}
                        pxClass={pxClass}
                        textClass="text-[16px]"
                    />
                </div>
            )}
        </div>
    );
}
