"use client";

import { useState } from "react";
import Image from "next/image";
import { useTranslations } from "next-intl";

interface SearchBarProps {
    placeholder: string;
    searchValue?: string;
    category: string;
    onSearch: (value: string, category: string) => void;
    iconSize?: number;
    pxClass?: string;
    textClass?: string;
}

const SearchBar = ({
    placeholder,
    searchValue,
    category,
    onSearch,
    iconSize = 24,
    pxClass = "px-2",
    textClass = "text-[20px]"
}: SearchBarProps) => {
    const t = useTranslations();
    const [value, setValue] = useState(searchValue || "");

    return (
        <div className={`flex flex-1 items-center ${pxClass} py-1`}>
            <input
                type="text"
                placeholder={placeholder}
                value={value}
                onChange={(e) => setValue(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && onSearch(value, category)}
                className={`border-none outline-none flex-1 bg-transparent px-2 pl-3 py-0 font-normal text-neutral-first placeholder-neutral-first/50 ${textClass}`}
            />

            <button
                onClick={() => onSearch(value, category)}
                className="pl-1 pr-3 text-neutral-first"
            >
                <Image
                    src="/images/common/search_icon.png"
                    width={iconSize}
                    height={iconSize}
                    alt={t('search')}
                />
            </button>
        </div>
    );
};

export default SearchBar;
