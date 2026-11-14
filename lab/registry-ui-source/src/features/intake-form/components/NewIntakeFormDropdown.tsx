'use client';

import { useClickOutside } from '@/shared/hooks';
import Image from 'next/image';
import { useRef, useState } from 'react';
import { useTranslations } from 'next-intl';
import { IntakeForm } from '../types/intake-form';

interface NewIntakeFormDropdownProps {
    forms?: IntakeForm[];
    onSelectForm?: (form: IntakeForm) => void;
}

export default function NewIntakeFormDropdown({
    forms = [],
    onSelectForm,
}: NewIntakeFormDropdownProps) {
    const [open, setOpen] = useState(false);
    const ref = useRef<HTMLDivElement>(null);
    const t = useTranslations();

    useClickOutside(ref, () => setOpen(false), open);

    return (
        <div ref={ref} className="relative mt-2 w-35 z-10">
            <button
                onClick={() => setOpen(o => !o)}
                className={`w-full flex items-center gap-2.5 px-4 py-1 bg-neutral-second border border-primary-second rounded-[10px] truncate ${open ? 'border-b-transparent rounded-b-none ' : ''}`}
                title={t('new_intake')}
            >
                <span className={`text-[16px] font-medium ${open ? 'text-neutral-first/50' : 'text-neutral-first'} truncate`}>
                    {t('new_intake')}
                </span>

                <Image
                    src="/images/common/down_arrow.png"
                    alt="open"
                    width={14}
                    height={8}
                    className={`transition-transform ${open ? 'rotate-180' : ''}`}
                />
            </button>

            {open && (
                <div className="absolute left-0 py-1 top-full w-full bg-neutral-second border border-primary-second border-t-0 rounded-b-[10px] overflow-hidden">
                    <div className="h-px bg-primary-second my-1" />
                    {forms.length === 0 && (
                        <div className="px-4 py-3 text-[16px] text-neutral-first truncate" title={t('no_options_available')}>
                            {t('no_options_available')}
                        </div>
                    )}

                    {forms.map(form => (
                        <DropdownItem
                            key={form.form_id}
                            label={form.form_mnemonic}
                            onClick={() => {
                                onSelectForm?.(form);
                                setOpen(false);
                            }}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}

function DropdownItem({
    label,
    onClick,
}: {
    label: string;
    onClick?: () => void;
}) {
    return (
        <div
            onClick={onClick}
            className="px-4 py-1 text-[16px] cursor-pointer hover:bg-secondary-first text-neutral-first font-medium truncate"
            title={label}
        >
            {label}
        </div>
    );
}
