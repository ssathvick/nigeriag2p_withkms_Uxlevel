'use client';

import Image from 'next/image';
import { useEffect, useRef, useState } from 'react';
import { useClickOutside } from '@/shared/hooks';

type Option = {
    label: string;
    value: string;
};

interface CustomDropdownProps {
    label?: string;
    options: Option[];
    value?: string;
    onChange?: (value: string) => void;
    loading?: boolean;
    placeholder?: string;
    disabled?: boolean;
}

export default function CustomDropdown({
    label,
    options,
    value,
    onChange,
    loading,
    placeholder = 'Select',
    disabled,
}: CustomDropdownProps) {
    const [open, setOpen] = useState(false);
    const [selected, setSelected] = useState<string | undefined>(value);

    const ref = useRef<HTMLDivElement>(null);
    useClickOutside(ref, () => setOpen(false), open);

    useEffect(() => {
        setSelected(value);
    }, [value]);

    const selectedItem = options.find((opt) => opt.value === selected);

    const handleSelect = (val: string) => {
        setSelected(val);
        setOpen(false);
        onChange?.(val);
    };

    return (
        <div className="w-full">
            {label && (
                <label
                    className="block text-[16px] font-medium text-neutral-first truncate"
                    title={label}
                >
                    {label}
                </label>
            )}

            <div ref={ref} className="relative mt-2">
                <div
                    onClick={() => !disabled && setOpen((prev) => !prev)}
                    className={`flex items-center justify-between gap-2.5 px-4 py-2 bg-neutral-second border border-primary-second rounded-[10px] truncate ${open ? 'border-b-transparent rounded-b-none' : ''}`}
                >
                    <span
                        className="text-[16px] truncate"
                        title={
                            loading
                                ? 'Loading...'
                                : selectedItem?.label || placeholder
                        }
                    >
                        {loading
                            ? 'Loading...'
                            : selectedItem?.label || placeholder}
                    </span>

                    <Image
                        src="/images/common/down_arrow.png"
                        alt="arrow"
                        width={14}
                        height={8}
                        className={`h-auto transition-transform ${open ? 'rotate-180' : ''}`}
                    />
                </div>

                {open && !disabled && (
                    <div className="absolute top-full left-0 w-full bg-neutral-second border border-primary-second border-t-0 rounded-b-[10px] z-20 max-h-60 overflow-auto">
                        {loading ? (
                            <div className="px-4 py-1 text-[16px]">Loading...</div>
                        ) : options.length === 0 ? (
                            <div className="px-4 py-1 text-[16px]">
                                No data available
                            </div>
                        ) : (
                            options.map((opt) => (
                                <div
                                    key={opt.value}
                                    onClick={() => handleSelect(opt.value)}
                                    className="px-4 py-1 text-[16px] cursor-pointer hover:bg-secondary-first truncate"
                                    title={opt.label}
                                >
                                    {opt.label}
                                </div>
                            ))
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}