'use client';

import { Check } from 'lucide-react';

interface Props {
    label: string;
    checked: boolean;
    onChange: (value: boolean) => void;
    disabled?: boolean;
}

export default function CheckboxField({
    label,
    checked,
    onChange,
    disabled = false,
}: Props) {
    return (
        <div className="flex items-center gap-3 select-none">
            <div
                onClick={() => !disabled && onChange(!checked)}
                className={`
                    w-5 h-5 rounded border transition-all flex items-center justify-center cursor-pointer
                    ${checked
                        ? 'bg-amber-600 border-amber-600 shadow-sm'
                        : 'bg-white border-secondary-second hover:border-amber-600/50'}
                    ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
                `}
            >
                {checked && <Check size={14} className="text-white" strokeWidth={3} />}
            </div>
            <label
                onClick={() => !disabled && onChange(!checked)}
                className={`block truncate text-sm font-semibold cursor-pointer ${disabled ? 'text-neutral-first/30' : 'text-neutral-first/70'}`}
                title={label}
            >
                {label}
            </label>
        </div>
    );
}
