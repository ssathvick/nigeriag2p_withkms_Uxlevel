"use client";

import { ValueInputProps } from "@/features/filter/types";

export default function TextFilterInput({
    value,
    onChange,
    placeholder,
}: ValueInputProps) {
    return (
        <input
            type="text"
            className="border border-secondary-second rounded-[10px] px-3 text-[16px] font-normal w-full outline-0 h-[36px] text-neutral-first/50 font-['Roboto']"
            placeholder={placeholder || "Search"}
            value={value || ""}
            onChange={e => onChange(e.target.value)}
        />
    );
}
