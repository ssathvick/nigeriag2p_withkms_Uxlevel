"use client";

import { ValueInputProps } from "@/features/filter/types";

export default function DateFilterInput({
    value,
    operator,
    onChange,
}: ValueInputProps) {
    if (operator === "between") {
        const [start, end] = Array.isArray(value) ? value : ["", ""];
        return (
            <div className="flex items-center gap-2 w-full font-['Roboto']">
                <input
                    type="date"
                    className="border border-secondary-second rounded-[10px] px-2 text-[16px] font-normal w-1/2 outline-0 h-[36px] text-neutral-first/50"
                    value={start || ""}
                    onChange={e => onChange([e.target.value, end])}
                />
                <span className="text-secondary-third">-</span>
                <input
                    type="date"
                    className="border border-secondary-second rounded-[10px] px-2 text-[16px] font-normal w-1/2 outline-0 h-[36px] text-neutral-first/50"
                    value={end || ""}
                    onChange={e => onChange([start, e.target.value])}
                />
            </div>
        );
    }

    return (
        <input
            type="date"
            className="border border-secondary-second rounded-[10px] px-3 text-[16px] font-normal w-full outline-0 h-[36px] text-neutral-first/50 font-['Roboto']"
            value={value || ""}
            onChange={e => onChange(e.target.value)}
        />
    );
}
