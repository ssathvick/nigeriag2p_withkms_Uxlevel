"use client";

import Image from "next/image";
import Link from "next/link";
import { useState } from "react";

import { prefixBasePath } from "@/shared/utils/path";

interface ViewAllProps {
    href: string;
    label?: string;
    bgColor?: string;
    hoverBgColor?: string;
    hoverTextColor?: string;
    textColor?: string;
}

export default function ViewAll({
    href,
    label = "View All",
    bgColor = "#F5F5F5",
    hoverBgColor,
    hoverTextColor,
    textColor = "#000000"
}: ViewAllProps) {
    const [isHovered, setIsHovered] = useState(false);

    return (
        <div className="flex justify-start ml-[30px] mt-[20px]">
            <Link
                href={href}
                className="lg:text-[12px] xl:text-[12px] 2xl:text-[14px] flex items-center font-semibold px-3 py-[4px] rounded-[15px] transition-colors duration-200"
                style={{
                    backgroundColor: isHovered && hoverBgColor ? hoverBgColor : bgColor,
                    color: isHovered && hoverTextColor ? hoverTextColor : textColor
                }}
                onMouseEnter={() => setIsHovered(true)}
                onMouseLeave={() => setIsHovered(false)}
            >
                {label}
                <Image
                    src={prefixBasePath("/right_arrow.png")}
                    alt="arrow"
                    width={12}
                    height={12}
                    className="ml-1.5"
                />
            </Link>
        </div>
    );
}
