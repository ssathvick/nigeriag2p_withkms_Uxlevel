"use client";

import { useState, useMemo } from "react";
import { useFilterConfig, normalizeNumericFilter } from "@/features/filter/utils";
import { AppliedFilters, FilterRule } from "@/features/filter/types";

export function useFilters(url: string) {
    const [appliedFilters, setAppliedFilters] = useState<AppliedFilters>([]);
    const { filterConfig, loading, error } = useFilterConfig(url);

    const applyFilters = (filters: AppliedFilters) => {
        setAppliedFilters(prev => {
            const map = new Map<string, FilterRule>();

            prev.forEach(f => {
                map.set(`${f.field_name}__${f.operator}`, f);
            });

            filters.forEach(f => {
                map.set(`${f.field_name}__${f.operator}`, f);
            });

            return Array.from(map.values());
        });
    };

    const filterBy = useMemo(() => {
        if (!appliedFilters.length) return "";

        const stableFilters = [...appliedFilters].sort((a, b) => {
            const aKey = `${a.field_name}__${a.operator}`;
            const bKey = `${b.field_name}__${b.operator}`;
            return aKey.localeCompare(bKey);
        });

        const configByField = Object.fromEntries(
            filterConfig.map(c => [c.field_name, c])
        );

        const result: Record<string, Record<string, unknown>> = {};

        for (const rule of stableFilters) {
            const field = rule.field_name;
            const operator = rule.operator;
            const cfg = configByField[field];
            const value = normalizeNumericFilter(
                cfg?.filter_type,
                operator,
                rule.value
            );

            if (!result[field]) result[field] = {};
            result[field][operator] = value;
        }

        return result;
    }, [appliedFilters, filterConfig]);


    const removeFilter = (index: number) => {
        setAppliedFilters(prev => prev.filter((_, i) => i !== index));
    };

    const clearAllFilters = () => setAppliedFilters([]);

    return {
        appliedFilters,
        filterBy,
        filterConfig,
        filterLoading: loading,
        applyFilters,
        removeFilter,
        clearAllFilters,
    };
}
