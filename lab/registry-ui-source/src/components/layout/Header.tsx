"use client";
import Image from "next/image";
import { useLocale, useTranslations } from 'next-intl';
import { useEffect, useState } from 'react';
import Link from 'next/link';

import { ProfileDropdown, NotificationDropdown, ConfigurationButton, LanguageSwitcher } from '@/components/layout';
import { useRuntimeConfig } from "@/context/RuntimeConfigContext";
import Can from "../shared/Can";
import { CONFIG_VIEW_ACTIONS } from "@/features/configuration/shared/utils/configurationView.actions";

export default function Header() {
    const t = useTranslations();
    const locale = useLocale();
    const { config } = useRuntimeConfig();
    const [isScrolled, setIsScrolled] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            setIsScrolled(window.scrollY > 0);
        };

        window.addEventListener("scroll", handleScroll);
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    return (
        <header className={`w-full bg-neutral-second fixed top-0 left-0 right-0 z-20 flex justify-center ${isScrolled ? "shadow-[0px_4px_10px_0px_rgba(0,0,0,0.15)]" : ""}`}>
            <div className="w-full h-17.5 flex items-center justify-between px-3">
                <Link href={`/${locale}`} className="flex shrink-0 min-w-20 items-center gap-2">
                    <Image
                        src={config?.registryLogo || "/images/common/openg2p_logo.png"}
                        alt="Registry Logo"
                        width={40}
                        height={40}
                        className="w-10 h-10 shrink-0 object-contain"
                        unoptimized
                    />
                    <div className="registry-header-title hidden sm:flex items-center gap-3">
                        <span
                            className="text-neutral-first text-[20px] font-medium not-italic leading-normal"
                            style={{ fontFamily: 'Roboto' }}
                        >
                            {config?.registryName ? t(config?.registryName) : t('registryGen2')}
                        </span>

                        {/* <span className="h-8 w-0.5 bg-secondary-second" />

                    <div className="flex flex-col leading-tight">
                        <span className="text-[14px] text-neutral-first/50">
                            powered by
                        </span>
                        <span className="text-[16px] font-medium text-neutral-first">
                            OpenG2P
                        </span>
                    </div> */}
                    </div>
                </Link>

                {/* Desktop Navigation */}
                <div className="flex min-w-0 items-center gap-2 sm:gap-8">
                    <Can anyOf={CONFIG_VIEW_ACTIONS}>
                        <ConfigurationButton />
                    </Can>
                    <LanguageSwitcher />
                    <NotificationDropdown />
                    <ProfileDropdown />
                </div>
            </div>
        </header>
    );
}
