'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { Palette, X, Save } from 'lucide-react';
import ThemeColorEditor from './ThemeColorEditor';
import { useTheme } from '@/features/configuration/registry/hooks/useTheme';
import { COLOR_ATTRIBUTES, THEME_ATTRIBUTES } from '@/features/configuration/registry/types';

interface CreateThemeModalProps {
    isOpen: boolean;
    onClose: () => void;
    onConfirm: (name: string, values: any[]) => Promise<void>;
}

export default function CreateThemeModal({
    isOpen,
    onClose,
    onConfirm,
}: CreateThemeModalProps) {
    const t = useTranslations();
    const { themes, themesLoading, loadAttributes } = useTheme();

    const [name, setName] = useState('');
    const [draftColors, setDraftColors] = useState<Record<string, string>>({});
    const [initializing, setInitializing] = useState(true);
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Initialize with factory theme values
    useEffect(() => {
        if (!isOpen) return;

        const initFactory = async () => {
            setInitializing(true);
            setName('');

            const factoryTheme = themes.find(th => th.is_factory_shipped);
            if (factoryTheme) {
                try {
                    const factoryAttrs = await loadAttributes(factoryTheme.theme_id);
                    const initialDraft: Record<string, string> = {};
                    factoryAttrs.forEach(attr => {
                        initialDraft[attr.attribute_name] = attr.attribute_value;
                    });
                    setDraftColors(initialDraft);
                } catch (error) {
                    console.error('Failed to load factory theme attributes', error);
                }
            } else {
                const defaults: Record<string, string> = {};
                COLOR_ATTRIBUTES.forEach(attr => {
                    defaults[attr.key] = '#EABB13';
                });
                setDraftColors(defaults);
            }
            setInitializing(false);
        };

        initFactory();
    }, [isOpen, themes, loadAttributes]);

    if (!isOpen) return null;

    const handleColorChange = (key: string, value: string) => {
        setDraftColors(prev => ({ ...prev, [key]: value }));
    };

    const getColor = (key: string): string => draftColors[key] || '';

    const handleSave = async () => {
        if (!name.trim() || isSubmitting) return;

        setIsSubmitting(true);
        try {
            const themeValues = THEME_ATTRIBUTES.map(attr => ({
                attribute_name: attr.key,
                attribute_value: getColor(attr.key) || (attr.key.includes('font') ? '' : '#EABB13')
            }));
            await onConfirm(name.trim(), themeValues);
        } finally {
            setIsSubmitting(false);
        }
    };

    const previewColors = COLOR_ATTRIBUTES.map(a => getColor(a.key));

    return (
        <div className="fixed inset-0 bg-neutral-first/80 z-[100] flex items-center justify-center p-4 font-roboto">
            <div className="relative w-full max-w-[1000px] max-h-[95vh] bg-primary-first rounded-[10px] overflow-hidden flex p-1">
                <div className="flex-1 w-full bg-neutral-second relative rounded-[10px] p-10 overflow-y-auto custom-scrollbar">

                    <button
                        onClick={onClose}
                        className="absolute top-6 right-6 text-secondary-third hover:text-neutral-first/70 transition-colors"
                    >
                        <X size={40} strokeWidth={2} />
                    </button>

                    <h2 className="text-2xl font-bold text-primary-second mb-1">{t('theme_config_new_theme')}</h2>
                    <p className="text-sm text-secondary-third mb-8">{t('theme_config_create_desc')}</p>

                    <div className="space-y-8">
                        {/* Name Input */}
                        <div>
                            <label className="block text-sm font-semibold text-neutral-first mb-2">
                                {t('theme_config_theme_name')}
                            </label>
                            <input
                                type="text"
                                value={name}
                                onChange={e => setName(e.target.value)}
                                placeholder={t('theme_config_create_placeholder')}
                                className="w-full px-4 py-2 border border-primary-second rounded-lg outline-none outline-1 outline-primary-second transition-all text-neutral-first/70 placeholder:text-secondary-third"
                                autoFocus
                            />
                        </div>

                        <ThemeColorEditor
                            selectedThemeId="NEW"
                            selectedTheme={{ theme_id: 'NEW', theme_mnemonic: name || t('theme_config_new_theme'), is_factory_shipped: false }}
                            attributesLoading={initializing}
                            previewColors={previewColors}
                            getColor={getColor}
                            onColorChange={handleColorChange}
                            onSave={handleSave}
                            onDiscard={onClose}
                            onDelete={() => { }}
                            onReset={() => { }}
                            isFactoryTheme={false}
                        />

                        {/* Action buttons */}
                        <div className="flex gap-4 pt-6 pb-2">
                            <button
                                onClick={onClose}
                                disabled={isSubmitting}
                                className="px-12 py-2.5 bg-secondary-third text-neutral-first rounded-[10px] hover:bg-secondary-third/80 transition-colors disabled:opacity-50 font-medium"
                            >
                                {t('theme_config_cancel')}
                            </button>
                            <button
                                onClick={handleSave}
                                disabled={!name.trim() || isSubmitting}
                                className="px-12 py-2.5 bg-neutral-first text-neutral-second rounded-[10px] hover:bg-neutral-first/90 transition-colors disabled:opacity-40 flex items-center gap-2 font-medium"
                            >
                                {isSubmitting && <div className="w-4 h-4 border-2 border-neutral-second border-t-transparent rounded-full animate-spin" />}
                                {t('theme_config_create')}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
