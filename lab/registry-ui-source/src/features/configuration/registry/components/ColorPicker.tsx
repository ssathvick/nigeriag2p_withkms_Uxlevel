'use client';

import { useTranslations } from 'next-intl';
import { useState, useRef, useEffect } from 'react';
import Image from 'next/image';
import { Check } from 'lucide-react';
import { useClickOutside } from '@/shared/hooks';

interface ColorPickerProps {
    value: string;
    onChange: (color: string) => void;
    label: string;
    id: string;
    disabled?: boolean;
}

const PRESET_COLORS = [
    '#EABB13', '#ED7C22', '#F3F1F4', '#E1E1E1', '#A1A1A1',
    '#EF4444', '#F97316', '#EAB308', '#22C55E', '#10B981',
    '#3B82F6', '#6366F1', '#8B5CF6', '#EC4899', '#14B8A6',
    '#1E293B', '#374151', '#6B7280', '#D1D5DB', '#FFFFFF',
];

export default function ColorPicker({ value, onChange, label, id, disabled = false }: ColorPickerProps) {
    const t = useTranslations();
    const [isOpen, setIsOpen] = useState(false);
    const [hex, setHex] = useState(value || '#000000');
    const panelRef = useRef<HTMLDivElement>(null);

    useClickOutside(panelRef, () => setIsOpen(false), isOpen);

    useEffect(() => {
        setHex(value || '#000000');
    }, [value]);

    const handleHexInput = (e: React.ChangeEvent<HTMLInputElement>) => {
        const v = e.target.value;
        setHex(v);
        if (/^#[0-9A-Fa-f]{6}$/.test(v)) {
            onChange(v);
        }
    };

    const handleNativeColorChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const v = e.target.value;
        setHex(v);
        onChange(v);
    };

    const handlePreset = (color: string) => {
        setHex(color);
        onChange(color);
    };

    if(disabled)return <div className="configuration-readonly-color"><span>{label}</span><output><span style={{backgroundColor:hex}} aria-hidden="true"/>{hex}</output></div>;
    return (
        <div className="flex flex-col gap-2">
            <div className="flex flex-col">
                <span className="text-[16px] font-medium text-neutral-first">{label}</span>
            </div>

            <div className="relative" ref={panelRef}>
                {/* Swatch trigger */}
                <div
                    id={id}
                    role="button" tabIndex={0} aria-label={label} aria-expanded={isOpen}
                    onKeyDown={e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();setIsOpen(!isOpen)}if(e.key==='Escape')setIsOpen(false)}}
                    onClick={() => !disabled && setIsOpen(!isOpen)}
                    className={`flex items-center gap-2.5 px-4 py-2 bg-neutral-second border border-primary-second rounded-[10px] cursor-pointer truncate ${isOpen ? 'border-b-transparent rounded-b-none' : ''} ${disabled ? 'opacity-50 cursor-not-allowed pointer-events-none' : ''}`}
                >
                    <span
                        className="w-5 h-5 rounded-sm border border-secondary-second shrink-0 shadow-inner"
                        style={{ backgroundColor: hex }}
                    />
                    <span className="text-[16px] font-mono text-neutral-first uppercase flex-1 text-left">{hex}</span>

                    {!disabled && (
                        <Image
                            src="/images/common/down_arrow.png"
                            alt="arrow"
                            width={14}
                            height={8}
                            className={`h-auto transition-transform ${isOpen ? 'rotate-180' : ''}`}
                        />
                    )}
                </div>

                {/* Dropdown panel */}
                {isOpen && (
                    <div className="absolute z-50 top-full left-0 bg-neutral-second rounded-b-[10px] shadow-xl border border-primary-second border-t-0 p-4 min-w-full w-max max-w-70">
                        {/* Native colour input */}
                        <div className="flex items-center gap-2 mb-4">
                            <label className="text-xs text-secondary-third shrink-0">{t('theme_config_custom')}</label>
                            <div className="flex-1 flex items-center gap-1.5 min-w-0">
                                <input
                                    type="color"
                                    value={hex}
                                    onChange={handleNativeColorChange}
                                    className="w-7 h-7 rounded-sm border border-secondary-second cursor-pointer p-0 bg-transparent overflow-hidden [&::-webkit-color-swatch-wrapper]:p-0 [&::-webkit-color-swatch]:border-none [&::-webkit-color-swatch]:rounded-sm"
                                />
                                <input
                                    type="text"
                                    value={hex}
                                    onChange={handleHexInput}
                                    maxLength={7}
                                    className="w-full text-sm font-mono px-2 h-7 rounded-md bg-secondary-first border border-secondary-second outline-none text-neutral-first uppercase"
                                />
                            </div>
                        </div>

                        {/* Preset grid */}
                        <div className="grid grid-cols-5 gap-2">
                            {PRESET_COLORS.map(color => (
                                <button
                                    key={color}
                                    type="button"
                                    onClick={() => handlePreset(color)}
                                    className="relative w-8 h-8 rounded-md border border-secondary-second hover:scale-110 transition-transform shrink-0 flex items-center justify-center"
                                    style={{ backgroundColor: color }}
                                    title={color}
                                >
                                    {hex.toLowerCase() === color.toLowerCase() && (
                                        <Check size={12} strokeWidth={3} className="text-neutral-first drop-shadow" />
                                    )}
                                </button>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
