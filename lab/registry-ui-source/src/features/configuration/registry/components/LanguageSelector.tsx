'use client';

import { useState, useRef } from 'react';
import { useTranslations } from 'next-intl';
import Image from 'next/image';
import { useClickOutside } from '@/shared/hooks';
import { Language } from '@/features/configuration/registry/types';

interface LanguageSelectorProps {
    languages: Language[];
    languagesLoading: boolean;
    selectedLanguageId: string | null;
    onSelectLanguage: (languageId: string) => void;
}

export default function LanguageSelector({
    languages,
    languagesLoading,
    selectedLanguageId,
    onSelectLanguage,
}: LanguageSelectorProps) {
    const t = useTranslations();
    const [isOpen, setIsOpen] = useState(false);
    const ref = useRef<HTMLDivElement>(null);

    useClickOutside(ref, () => setIsOpen(false), isOpen);

    const selectedLanguage = languages.find(l => l.language_id === selectedLanguageId);

    const handleSelect = (id: string) => {
        onSelectLanguage(id);
        setIsOpen(false);
    };

    return (
        <div className="relative w-full" ref={ref}>
            <div
                onClick={() => !languagesLoading && setIsOpen(!isOpen)}
                className={`flex items-center justify-between gap-2.5 px-4 py-2 bg-neutral-second border border-primary-second rounded-[10px] cursor-pointer truncate ${isOpen ? 'border-b-transparent rounded-b-none' : ''}`}
            >
                <div className="flex items-center gap-2 truncate">
                    {selectedLanguage?.language_flag_base64 && (
                        <div className="w-6 h-4 relative rounded-sm overflow-hidden shrink-0 border">
                            <Image
                                src={selectedLanguage.language_flag_base64}
                                alt={selectedLanguage.language_label}
                                fill
                                className="object-cover"
                            />
                        </div>
                    )}
                    <span className="text-[16px] font-medium text-neutral-first truncate">
                        {languagesLoading ? 'Loading...' : selectedLanguage?.language_label || t('select_language')}
                    </span>
                </div>

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
                    {languages.length === 0 && !languagesLoading ? (
                        <div className="px-4 py-2 text-[16px] text-secondary-third">
                            {t('no_items_found')}
                        </div>
                    ) : (
                        languages.map(lang => (
                            <div
                                key={lang.language_id}
                                onClick={() => handleSelect(lang.language_id)}
                                className={`flex items-center gap-2 px-4 py-2 text-[16px] cursor-pointer hover:bg-secondary-first truncate transition-colors ${selectedLanguageId === lang.language_id ? 'bg-primary-first/10 font-semibold text-primary-second' : 'text-neutral-first'}`}
                            >
                                {lang.language_flag_base64 && (
                                    <div className="w-6 h-4 relative rounded-sm overflow-hidden shrink-0 border">
                                        <Image
                                            src={lang.language_flag_base64}
                                            alt={lang.language_label}
                                            fill
                                            className="object-cover"
                                        />
                                    </div>
                                )}
                                <span className="truncate">{lang.language_label}</span>
                            </div>
                        ))
                    )}
                </div>
            )}
        </div>
    );
}
