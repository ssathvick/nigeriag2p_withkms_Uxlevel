'use client';

import { ChevronDown } from 'lucide-react';

type Option = {
    label: string;
    value: string;
};

interface FilterSelectProps {
    options: Option[];
    value: string;
    onChange: (value: string) => void;
    disabled?: boolean;
    loading?: boolean;
    placeholder?: string;
    className?: string;
}

export default function FilterSelect({
    options,
    value,
    onChange,
    disabled,
    loading,
    placeholder,
    className = '',
}: FilterSelectProps) {
    const isDisabled = disabled || loading;

    return (
        <div className={`relative w-full ${className}`}>
            <select
                value={value}
                onChange={(e) => onChange(e.target.value)}
                disabled={isDisabled}
                className="w-full appearance-none border border-primary-second rounded-[10px] bg-neutral-second py-2 pl-4 pr-9 text-[16px] text-neutral-first outline-none focus:outline-none focus:ring-0 focus-visible:ring-0 focus:border-primary-second disabled:cursor-not-allowed disabled:opacity-50"
            >
                {placeholder && !value && (
                    <option value="" disabled>
                        {loading ? 'Loading...' : placeholder}
                    </option>
                )}
                {options.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                        {opt.label}
                    </option>
                ))}
            </select>
            <ChevronDown
                size={18}
                className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-neutral-first/50"
                aria-hidden
            />
        </div>
    );
}
