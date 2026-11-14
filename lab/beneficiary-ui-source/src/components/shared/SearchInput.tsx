"use client";

import Image from "next/image";
import { useState } from "react";
import { prefixBasePath } from "@/shared/utils/path";

interface SearchInputProps {
    onSearch: (value: string) => void;
    placeholder?: string;
    className?: string;
    bgColor?: string;
}

export default function SearchInput({
    onSearch,
    placeholder = "Search",
    className = "",
    bgColor = "bg-gray-100",
}: SearchInputProps) {

    const [value, setValue] = useState("");

    function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
        const val = e.target.value;
        setValue(val);

        if (val.trim() === "") {
            onSearch("");
        }
    }

    return (
        <div className={`relative ${className}`}>
            <input
                type="text"
                placeholder={placeholder}
                value={value}
                onChange={handleChange}
                className={`w-full py-2 px-4 text-black rounded-[20px] focus:outline-none ${bgColor}`}
            />
            <span
                className="absolute right-4 top-1/2 -translate-y-1/2 cursor-pointer"
                onClick={() => onSearch(value)}
            >
                <Image
                    src={prefixBasePath("/search.png")}
                    alt="Search"
                    width={20}
                    height={20}
                />
            </span>
        </div>
    );
}
