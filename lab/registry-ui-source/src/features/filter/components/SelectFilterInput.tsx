"use client";

import Image from "next/image";
import { SelectOption, ValueInputProps } from "@/features/filter/types";
import { useTranslations } from "next-intl";

interface SelectFilterInputProps extends ValueInputProps {
    options_source?: SelectOption[];
}

export default function SelectFilterInput({
    value,
    operator,
    onChange,
    options_source = [],
}: SelectFilterInputProps) {
    const t = useTranslations();
    const isMultiSelect = operator === "in" || operator === "nin";

    const handleMultiSelectChange = (optionValue: string) => {
        const currentValues = Array.isArray(value) ? value : [];

        if (currentValues.includes(optionValue)) {
            onChange(currentValues.filter(v => v !== optionValue));
        } else {
            onChange([...currentValues, optionValue]);
        }
    };

    if (isMultiSelect) {
        const selectedValues = Array.isArray(value) ? value : [];

        return (
            <div className="border border-secondary-second rounded-[10px] p-3 w-full space-y-2 font-['Roboto'] overflow-y-auto max-h-[100px]">
                {options_source.length === 0 ? (
                    <p className="text-sm text-neutral-first/50">{t("no_options_available")}</p>
                ) : (
                    options_source.map(opt => (
                        <label
                            key={opt.value}
                            className="flex items-center gap-2 cursor-pointer hover:bg-neutral-first/5 p-1 px-2 rounded"
                        >
                            <input
                                type="checkbox"
                                checked={selectedValues.includes(opt.value)}
                                onChange={() => handleMultiSelectChange(opt.value)}
                                className="rounded border-secondary-third h-4 w-4"
                            />
                            <span className="text-[16px] font-normal text-neutral-first">{opt.label}</span>
                        </label>
                    ))
                )}
            </div>
        );
    }

    return (
        <div className="relative w-full font-['Roboto']">
            <select
                className="border border-secondary-second rounded-[10px] px-3 text-[16px] font-normal w-full appearance-none bg-neutral-second pr-10 outline-0 h-[36px] text-neutral-first/50"
                value={value || ""}
                onChange={e => onChange(e.target.value)}
            >
                <option value="">{t("common.select")}</option>
                {options_source.map(opt => (
                    <option key={opt.value} value={opt.value}>
                        {opt.label}
                    </option>
                ))}
            </select>
            <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
                <Image
                    src="/images/common/down_arrow.png"
                    alt=""
                    width={14}
                    height={14}
                    className="h-auto"
                />
            </div>
        </div>
    );
}
