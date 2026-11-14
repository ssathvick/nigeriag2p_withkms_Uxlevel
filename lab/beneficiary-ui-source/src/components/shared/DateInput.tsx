"use client";

import Image from "next/image";
import { prefixBasePath } from "@/shared/utils/path";

interface DateInputProps {
    value: string;
    onChange: (value: string) => void;
    placeholder?: string;
    className?: string;
    onIconClick?: () => void;
    bgColor?: string;
}

export default function DateInput({
    value,
    onChange,
    placeholder = "Select Date",
    className = "",
    onIconClick,
    bgColor = "bg-white",
}: DateInputProps) {
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
                    src={prefixBasePath("/date.png")}
                    alt="Date"
                    width={20}
                    height={20}
                />
            </span>
        </div>
    );
}
