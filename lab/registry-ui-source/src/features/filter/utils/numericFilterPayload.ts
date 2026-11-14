import type { FilterType } from "@/features/filter/types";

export function parseOptionalNumber(raw: unknown): number | "" {
    if (raw === "" || raw === null || raw === undefined) return "";
    if (typeof raw === "number") return Number.isFinite(raw) ? raw : "";
    const n = Number(String(raw).trim());
    return Number.isFinite(n) ? n : "";
}

export function normalizeNumericFilter(
    filterType: FilterType | undefined,
    operator: string,
    value: unknown
): unknown {
    if (filterType !== "number_range") return value;
    if (operator === "between" && Array.isArray(value)) {
        return value.map(v => parseOptionalNumber(v));
    }
    return parseOptionalNumber(value);
}
