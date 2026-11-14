"use client";
import Image from "next/image";

import { prefixBasePath } from '@/shared/utils/path';
import { LanguageDropdown, ProfileDropdown, NotificationDropdown, DepartmentDropdown } from '@/components/layout';
import { useRuntimeConfig } from "@/context/RuntimeConfigContext";

export default function Header() {
    const { multiDepartmentEnabled } = useRuntimeConfig();
    return (
        <header className="w-full bg-white flex items-center justify-between px-3 py-3 fixed top-0 left-0 right-0 z-20 h-[70px] border-b border-gray-300 shadow-[0px_4px_10px_0px_#00000026]">
            <div className="flex items-center gap-3">
                <Image
                    src={prefixBasePath("/openg2p_logo.png")}
                    alt="Openg2p Logo"
                    width={40}
                    height={40}
                />
                <span className="text-[20px] font-[500] text-black">
                    Beneficiary Portal
                </span>
                {multiDepartmentEnabled && <DepartmentDropdown />}
            </div>

            <div className="flex items-center gap-6">
                <button
                    onClick={() => console.log("Redirect to Help page")}
                >
                    <span className="text-[16px] font-[400] text-black">
                        Help?
                    </span>
                </button>
                <LanguageDropdown />
                <NotificationDropdown />
                <ProfileDropdown />
            </div>
        </header>
    );
}
