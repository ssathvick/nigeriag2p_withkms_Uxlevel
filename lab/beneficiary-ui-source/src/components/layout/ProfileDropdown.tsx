"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { useLocale, useTranslations } from "next-intl";

import { useAuth } from "@/context/GlobalContext";

import { prefixBasePath, prefixBaseApiPath } from "@/shared/utils/path";
import { useClickOutside } from "@/shared/hooks/useClickOutside";

export default function ProfileDropdown() {
    const [open, setOpen] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);
    const { profile, setProfile } = useAuth();
    const router = useRouter();
    const lang = useLocale();
    const t = useTranslations();

    const toggleDropdown = () => setOpen((prev) => !prev);

    const logoutHandler = async () => {
        try {
            await fetch(prefixBaseApiPath("/auth/logout"), { method: "POST" });
        } finally {
            setProfile(null);
            router.push(`/${lang}/login`);
        }
    };

    useClickOutside(dropdownRef, () => setOpen(false), open);

    const avatarSrc = profile?.picture || prefixBasePath("/user_image.png");

    return (
        <div ref={dropdownRef} className="relative">
            <button
                onClick={toggleDropdown}
                className="flex items-center gap-2 px-3 py-1 bg-white text-sm font-medium text-gray-800 rounded-md transition cursor-pointer"
            >
                <span className="text-[16px] text-black">
                    Hi, <span className="font-[500]">{profile?.name || "User"}</span>
                </span>

                <div className="w-8 h-8 rounded-full overflow-hidden shadow-xl border-2 border-gray-300">
                    <Image
                        src={avatarSrc}
                        alt="User Avatar"
                        width={38}
                        height={38}
                        className="object-cover"
                    />
                </div>
            </button>

            {open && (
                <div className="absolute right-0 top-10 mt-3 w-35 bg-white border border-gray-200 rounded-lg shadow-xl z-50 flex flex-col">
                    <div className="absolute -top-2.5 right-9 w-5 h-5 bg-white border-l border-t border-gray-200 rotate-45"></div>

                    <div className="flex flex-col">
                        <Link
                            href={`/${lang}/myprofile`}
                            onClick={() => setOpen(false)}
                            className="flex items-center gap-x-2 px-4 py-4 text-sm text-black font-bold"
                        >
                            <Image
                                src={prefixBasePath("/user_dropdown.png")}
                                alt="My Profile"
                                width={13}
                                height={15}
                            />
                            {t("profileDropdown.myProfile")}
                        </Link>

                        <button
                            onClick={logoutHandler}
                            className="flex items-center gap-x-2 px-4 pb-4 text-sm text-black font-bold"
                        >
                            <Image
                                src={prefixBasePath("/logout.png")}
                                alt="Logout"
                                width={18}
                                height={18}
                            />
                            {t("profileDropdown.logout")}
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
