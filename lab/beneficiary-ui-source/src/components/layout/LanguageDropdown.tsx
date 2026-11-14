"use client";

import { useState, useRef } from "react";
import Image from "next/image";
import { useLocale } from "next-intl";
import { useRouter, usePathname } from "next/navigation";

import { prefixBasePath } from "@/shared/utils/path";
import { getSupportedLocales } from "@/shared/utils/lang";
import { useClickOutside } from "@/shared/hooks/useClickOutside";

const localeMap: Record<string, { name: string; flag: string }> = {
    en: { name: "English", flag: "/flag_en.png" },
    fr: { name: "Français", flag: "/flag_fr.png" },
    tl: { name: "Tagalog", flag: "/flag_tl.png" },
};

export default function LanguageDropdown() {
    const currentLocale = useLocale();
    const supportedLocales = getSupportedLocales();
    const router = useRouter();
    const pathname = usePathname();

    const [open, setOpen] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);

    const toggleDropdown = () => setOpen((prev) => !prev);

    const selectLanguage = (locale: string) => {
        setOpen(false);
        const newPath = pathname.replace(`/${currentLocale}`, `/${locale}`);
        router.push(newPath);
    };

    useClickOutside(dropdownRef, () => setOpen(false), open);

    return (
        <div className="relative w-fit select-none text-sm" ref={dropdownRef}>
            <div
                className="flex justify-between items-center rounded-[15px] px-4 py-2 cursor-pointer transition-all duration-300 hover:bg-[#EBEBEB]"
                onClick={toggleDropdown}
            >
                <div className="flex items-center gap-2">
                    <Image
                        src={prefixBasePath(localeMap[currentLocale].flag)}
                        alt={localeMap[currentLocale].name}
                        width={27}
                        height={18}
                        className="rounded-sm"
                    />
                    <span className="text-[16px] font-medium text-black whitespace-nowrap">
                        {localeMap[currentLocale].name}
                    </span>
                </div>

                <Image
                    src={prefixBasePath("/arrow_02.png")}
                    alt="Open"
                    width={14}
                    height={14}
                    className={`ml-3 transition-transform duration-300 ${open ? "rotate-180" : ""}`}
                />
            </div>

            <div
                className={`absolute top-0 left-0 bg-white rounded-xl shadow-lg border border-gray-100 z-20 min-w-[150px] overflow-hidden transition-all duration-300 ease-in-out
                    ${open ? "opacity-100 translate-y-0 pointer-events-auto" : "opacity-0 -translate-y-2 pointer-events-none"}
                `}
            >
                <div className="flex justify-between items-center px-4 py-2">
                    <span className="text-black font-semibold text-sm">Languages</span>
                    <button
                        onClick={toggleDropdown}
                        className="p-1 rounded-full transition-colors duration-200 hover:bg-gray-100"
                    >
                        <Image
                            src={prefixBasePath("/arrow_02.png")}
                            alt="Close"
                            width={14}
                            height={14}
                            className="rotate-180 transition-transform duration-300"
                        />
                    </button>
                </div>

                <div className="py-2 px-2">
                    {supportedLocales.map((locale) => (
                        <div
                            key={locale}
                            onClick={() => selectLanguage(locale)}
                            className={`flex items-center gap-3 py-2.5 px-3 rounded-lg cursor-pointer transition-all duration-300 hover:bg-orange-50 group
                                ${currentLocale === locale ? "bg-orange-50" : ""}
                            `}
                        >
                            <span className="w-1.5 h-1.5 rounded-full bg-orange-500 flex-shrink-0 transition-transform duration-300 group-hover:scale-125"></span>

                            <div className="flex items-center gap-2">
                                <Image
                                    src={prefixBasePath(localeMap[locale].flag)}
                                    alt={localeMap[locale].name}
                                    width={24}
                                    height={16}
                                />
                                <span
                                    className={`text-sm transition-colors duration-300
                                        ${currentLocale === locale ? "font-medium text-orange-600" : "text-gray-700"}
                                    `}
                                >
                                    {localeMap[locale].name}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
