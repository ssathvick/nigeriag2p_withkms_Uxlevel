'use client';

import { useState, useRef, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import Image from 'next/image';
import { useClickOutside } from '@/shared/hooks';
import { Theme } from '@/features/configuration/registry/types';

interface ThemeSelectorProps {
    themes: Theme[];
    themesLoading: boolean;
    selectedThemeId: string | null;
    onSelectTheme: (themeId: string) => void;
}

export default function ThemeSelector({
    themes,
    themesLoading,
    selectedThemeId,
    onSelectTheme,
}: ThemeSelectorProps) {
    const t = useTranslations();
    const [isOpen, setIsOpen] = useState(false);
    const ref = useRef<HTMLDivElement>(null);

    useClickOutside(ref, () => setIsOpen(false), isOpen);

    const selectedTheme = themes.find(t => t.theme_id === selectedThemeId);

    const handleSelect = (id: string) => {
        onSelectTheme(id);
        setIsOpen(false);
    };

    return (
        <div className="relative w-full" ref={ref}>
            <div
                onClick={() => !themesLoading && setIsOpen(!isOpen)}
                className={`flex items-center justify-between gap-2.5 px-4 py-2 bg-neutral-second border border-primary-second rounded-[10px] cursor-pointer truncate ${isOpen ? 'border-b-transparent rounded-b-none' : ''}`}
            >
                <span className="text-[16px] font-medium text-neutral-first truncate">
                    {themesLoading ? 'Loading...' : selectedTheme?.theme_mnemonic || t('theme_config_select_theme')}
                </span>

                <Image
                    src="/images/common/down_arrow.png"
                    alt="arrow"
                    width={14}
                    height={8}
                    className={`h-auto transition-transform ${isOpen ? 'rotate-180' : ''}`}
                />
            </div>

            {isOpen && (
                <div className="absolute z-50 top-full left-0 bg-neutral-second rounded-b-[10px] shadow-xl border border-primary-second border-t-0 min-w-full overflow-auto">
                    {themes.length === 0 && !themesLoading ? (
                        <div className="px-4 py-2 text-[16px] text-secondary-third">
                            {t('theme_config_no_themes')}
                        </div>
                    ) : (
                        themes.map(theme => (
                            <div
                                key={theme.theme_id}
                                onClick={() => handleSelect(theme.theme_id)}
                                className={`px-4 py-2 text-[16px] cursor-pointer hover:bg-secondary-first truncate transition-colors ${selectedThemeId === theme.theme_id ? 'bg-primary-first/10 font-semibold text-primary-second' : 'text-neutral-first'}`}
                            >
                                {theme.theme_mnemonic}
                            </div>
                        ))
                    )}
                </div>
            )}
        </div>
    );
}
