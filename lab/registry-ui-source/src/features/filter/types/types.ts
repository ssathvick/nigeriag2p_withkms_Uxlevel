export type FilterType =
    | "text"
    | "dropdown"
    | "date_range"
    | "number_range"
    | "boolean";

export interface SelectOption {
    value: string;
    label: string;
}

export interface FilterConfig {
    field_name: string;
    display_label: string;
    filter_type: FilterType;
    order: number;
    allowed_operators: string[];
    options_source?: SelectOption[];
}

export interface FilterRule {
    field_name: string;
    operator: string;
    value: string | number | boolean | null | string[] | number[];
}

export type AppliedFilters = FilterRule[];

export interface ValueInputProps {
    value: any;
    operator: string;
    onChange: (value: any) => void;
    placeholder?: string;
}
