'use client';

import { useClickOutside } from "@/shared/hooks";
import Image from "next/image";
import { useEffect, useRef, useState } from "react";
import { useTranslations } from "next-intl";

interface CapsuleDropdownProps {
    label: string;
    items: string[];
    value?: string;
    onChange?: (value: string) => void;
    onOpen?: () => void;
    emptyMessage?: string;
    maxWidth?: string;
}

export default function CapsuleDropdown(props: CapsuleDropdownProps) {
    const t = useTranslations();
    const { label, items, value, onChange, onOpen, emptyMessage, maxWidth } = props;
    const fallbackEmptyMessage = emptyMessage || t('no_items_available');

    const [open, setOpen] = useState(false);
    const [selected, setSelected] = useState<string | undefined>(undefined);

    const dropdownRef = useRef<HTMLDivElement>(null);

    useClickOutside(dropdownRef, () => setOpen(false), open);

    useEffect(() => {
        if (value !== undefined) {
            setSelected(value);
        } else {
            setSelected(undefined);
        }
    }, [value]);

    function handleSelect(value: string) {
        setSelected(value);
        setOpen(false);
        onChange?.(value);
    }

    function handleToggle() {
        if (!open) {
            onOpen?.();
        }
        setOpen(!open);
    }

    return (
        <div className="flex items-center gap-3">
            <span className="text-[16px] w-25 text-neutral-first font-medium whitespace-nowrap truncate" title={label}>
                {label}
            </span>

            <div ref={dropdownRef} className={`relative z-10 ${maxWidth || 'w-35'}`}>
                <div
                    onClick={handleToggle}
                    className={`w-full flex items-center justify-between gap-2.5 px-4 py-1 bg-neutral-second border border-primary-second rounded-[10px] truncate ${open ? 'border-b-transparent rounded-b-none ' : ''}`}
                    title={selected}
                >
                    <span className={`text-[16px] font-medium ${open ? 'text-neutral-first/50' : 'text-neutral-first'} truncate`}>
                        {selected ?? t('select')}
                    </span>

                    <Image
                        src="/images/common/down_arrow.png"
                        alt="open"
                        width={14}
                        height={8}
                        className={`h-auto transition-transform ${open ? 'rotate-180' : ''}`}
                    />
                </div>

                {open && (
                    <div className="absolute left-0 py-1 top-full w-full bg-neutral-second border border-primary-second border-t-0 rounded-b-[10px] overflow-hidden">
                        {(
                            items.length === 0 ?
                                (
                                    <div className="px-4 py-3 text-[16px] text-neutral-first truncate" title={fallbackEmptyMessage}>
                                        {fallbackEmptyMessage}
                                    </div>
                                )
                                : (
                                    items.map((item) => (
                                        <div
                                            key={item}
                                            onClick={() => handleSelect(item)}
                                            className="px-4 py-1 text-[16px] cursor-pointer hover:bg-secondary-first text-neutral-first font-medium truncate"
                                            title={item}
                                        >
                                            {item}
                                        </div>
                                    ))
                                )
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
