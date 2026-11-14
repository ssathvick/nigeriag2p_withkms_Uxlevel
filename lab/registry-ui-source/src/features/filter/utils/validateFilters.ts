import { FilterRule, FilterConfig } from "@/features/filter/types";

export interface FilterError {
    filterId: string;
    message: string;
}

export function validateFilters(
    filters: FilterRule[],
    configMap: Record<string, FilterConfig>
): FilterError[] {
    const errors: FilterError[] = [];

    for (const filter of filters) {
        const config = configMap[filter.field_name];
        if (!config) continue;
    }

    return errors;
}
