"use client";

import { ValueInputProps } from "@/features/filter/types";
import { parseOptionalNumber } from "@/features/filter/utils";

export default function NumberFilterInput({
    value,
    operator,
    onChange,
}: ValueInputProps) {
    if (operator === "between") {
        const [min, max] = Array.isArray(value) ? value : ["", ""];
        return (
            <div className="flex items-center gap-2 w-full font-['Roboto']">
                <input
                    type="number"
                    className="border border-secondary-second rounded-[10px] px-3 text-[16px] font-normal w-1/2 outline-0 h-[36px] text-neutral-first/50"
                    placeholder="Min"
                    value={min === "" || min === null || min === undefined ? "" : min}
                    onChange={e =>
                        onChange([parseOptionalNumber(e.target.value), parseOptionalNumber(max)])
                    }
                />
                <span className="text-secondary-third">-</span>
                <input
                    type="number"
                    className="border border-secondary-second rounded-[10px] px-3 text-[16px] font-normal w-1/2 outline-0 h-[36px] text-neutral-first/50"
                    placeholder="Max"
                    value={max === "" || max === null || max === undefined ? "" : max}
                    onChange={e =>
                        onChange([parseOptionalNumber(min), parseOptionalNumber(e.target.value)])
                    }
                />
            </div>
        );
    }

    return (
        <input
            type="number"
            className="border border-secondary-second rounded-[10px] px-3 text-[16px] font-normal w-full outline-0 h-[36px] text-neutral-first/50 font-['Roboto']"
            value={value === "" || value === null || value === undefined ? "" : value}
            onChange={e => onChange(parseOptionalNumber(e.target.value))}
        />
    );
}
