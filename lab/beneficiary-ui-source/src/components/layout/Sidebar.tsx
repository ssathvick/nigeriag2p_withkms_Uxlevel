"use client";

import { useState, useRef } from "react";

import Image from "next/image";
import Link from "next/link";
import { useLocale } from "next-intl";
import { usePathname } from "next/navigation";

import { getMenuItems, getRouteToIndex } from '@/shared/utils/navigation';
import { prefixBasePath } from '@/shared/utils/path';
import { useClickOutside } from "@/shared/hooks/useClickOutside";


interface SidebarProps {
    onItemClick?: (index: number, href: string) => void;
}

export default function Sidebar({ onItemClick }: SidebarProps) {
    const [expanded, setExpanded] = useState(false);
    const locale = useLocale();
    const pathname = usePathname();
    const sidebarRef = useRef<HTMLDivElement>(null);


    const menuItems = getMenuItems(locale);
    const routeToIndex = getRouteToIndex(locale);

    const activeItem =
        Object.entries(routeToIndex).find(([href]) =>
            pathname.startsWith(href)
        )?.[1];

    const handleItemClick = (index: number, href: string) => {
        if (onItemClick) {
            onItemClick(index, href);
        }
    };

    useClickOutside(sidebarRef, () => setExpanded(false), expanded);

    return (
        <div
            ref={sidebarRef}
            className={`bg-[#FCBE00] border-r border-gray-100 fixed top-[70px] left-0 bottom-0 transition-all duration-300 ease-in-out ${expanded ? "w-[250px]" : "w-[60px]"} z-20`}
        >
            <div className="flex items-center justify-center h-16">
                {!expanded ? (
                    <button
                        className="px-2 rounded-lg transition-colors"
                        onClick={() => setExpanded(true)}
                    >
                        <Image
                            src={prefixBasePath("/menu.png")}
                            alt="Menu"
                            width={24}
                            height={24}
                        />
                    </button>
                ) : (
                    <div className="flex items-center justify-between w-full px-4">
                        <span className="font-[600] text-[20px] text-black">Menu</span>
                        <button
                            className="px-1 rounded transition-colors"
                            onClick={() => setExpanded(false)}
                        >
                            <Image
                                src={prefixBasePath("/close.png")}
                                alt="Close"
                                width={20}
                                height={20}
                                priority
                            />
                        </button>
                    </div>
                )}
            </div>

            <div>
                {menuItems.map((item, idx) => {
                    const isActive = idx === activeItem;

                    return (
                        <Link
                            key={idx}
                            href={item.href}
                            className={`flex items-center text-black text-[16px] font-[500] cursor-pointer transition-all duration-200 pl-1.5 mb-5
                                ${isActive ? "bg-white/40" : "hover:bg-white/20"}
                            `}
                            onClick={() => handleItemClick(idx, item.href)}
                        >
                            <div className="flex-shrink-0 w-12 h-12 flex items-center justify-center">
                                <Image
                                    src={prefixBasePath(item.icon)}
                                    alt={item.name}
                                    width={30}
                                    height={30}
                                    className="w-auto h-auto"
                                />
                            </div>

                            <span
                                className={`transition-all duration-300 ease-in-out whitespace-nowrap overflow-hidden ${expanded ? "opacity-100 max-w-full ml-2" : "opacity-0 max-w-0 ml-0"}`}
                            >
                                {item.name}
                            </span>
                        </Link>
                    );
                })}
            </div>
        </div>
    );
}
