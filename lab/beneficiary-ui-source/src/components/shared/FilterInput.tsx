"use client";

import Image from "next/image";
import { prefixBasePath } from "@/shared/utils/path";

interface FilterInputProps {
    value: string;
    onChange: (value: string) => void;
    placeholder?: string;
    className?: string;
    onIconClick?: () => void;
    bgColor?: string;
}

export default function FilterInput({
    value,
    onChange,
    placeholder = "Filter",
    className = "",
    onIconClick,
    bgColor = "bg-white",
}: FilterInputProps) {
    return (
        <div className={`relative ${className}`}>
            <input
                type="text"
                placeholder={placeholder}
                value={value}
                onChange={(e) => onChange(e.target.value)}
                className={`w-full py-2 px-4 text-black rounded-[20px] focus:outline-none ${bgColor}`}
            />
            <span
                className="absolute right-3 top-1/2 -translate-y-1/2 cursor-pointer"
                onClick={onIconClick}
            >
                <Image
                    src={prefixBasePath("/filter.png")}
                    alt="Filter"
                    width={20}
                    height={20}
                />
            </span>
        </div>
    );
}
