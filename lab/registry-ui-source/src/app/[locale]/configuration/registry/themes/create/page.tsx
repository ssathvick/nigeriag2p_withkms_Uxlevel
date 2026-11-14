'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { Palette, ArrowLeft, Save, X } from 'lucide-react';
import { toast } from 'react-toastify';
import { useRouter } from '@/i18n/navigation';
import { TopBar } from '@/components/shared';
import ThemeColorEditor from '@/features/configuration/registry/components/ThemeColorEditor';
import { useTheme } from '@/features/configuration/registry/hooks/useTheme';
import { COLOR_ATTRIBUTES, THEME_ATTRIBUTES } from '@/features/configuration/registry/types';

const CreateThemePage = () => {
    const t = useTranslations();
    const router = useRouter();
    const {
        themes,
        themesLoading,
        createTheme,
        loadAttributes,
    } = useTheme();

    const [name, setName] = useState('');
    const [draftColors, setDraftColors] = useState<Record<string, string>>({});
    const [initializing, setInitializing] = useState(true);

    // Initialize with factory theme values
    useEffect(() => {
        const initFactory = async () => {
            if (themesLoading) return;

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
                    defaults[attr.key] = '#ffffff';
                });
                setDraftColors(defaults);
            }
            setInitializing(false);
        };

        initFactory();
    }, [themes, themesLoading, loadAttributes]);

    const handleColorChange = (key: string, value: string) => {
        setDraftColors(prev => ({ ...prev, [key]: value }));
    };

    const getColor = (key: string): string => draftColors[key] || '';

    const handleSave = async () => {
        if (!name.trim()) {
            toast.error(t('theme_config_name_required'));
            return;
        }

        const themeValues = THEME_ATTRIBUTES.map(attr => ({
            attribute_name: attr.key,
            attribute_value: getColor(attr.key) || (attr.key.includes('font') ? '' : '#EABB13')
        }));

        const result = await createTheme(name.trim(), themeValues);
        if (result !== null) {
            toast.success(t('theme_config_create_success'));
            router.push('/configuration/registry/themes');
        } else {
            toast.error(t('theme_config_create_error'));
        }
    };

    const previewColors = COLOR_ATTRIBUTES.map(a => getColor(a.key));

    return (
        <>
            <TopBar
                breadcrumb={[
                    { label: t('registry') },
                    { label: t('registry_theme'), href: '/configuration/registry/theme' },
                    { label: t('theme_config_new_theme') }
                ]}
                showFilters={false}
                showPagination={false}
                showAddNewButton={false}
            />

            <div className="mx-7.5 flex flex-col gap-5 pb-10 font-roboto">
                {/* Header card */}
                <div className="bg-neutral-second rounded-[10px] p-6 flex items-center justify-between gap-4">
                    <div className="flex items-center gap-4">
                        <button
                            onClick={() => router.back()}
                            className="w-9 h-9 rounded-[10px] bg-secondary-first hover:bg-secondary-second flex items-center justify-center transition-colors"
                        >
                            <ArrowLeft size={20} className="text-neutral-first" />
                        </button>
                        <div className="flex items-center gap-3">

                            <div>
                                <h1 className="text-lg font-semibold text-neutral-first m-0">{t('theme_config_new_theme')}</h1>
                            </div>
                        </div>
                    </div>

                    <div className="flex items-center gap-3">
                        <button
                            onClick={() => router.back()}
                            className="px-5 h-8.5 rounded-[10px] bg-secondary-second text-neutral-first/70 text-sm font-semibold hover:bg-secondary-third transition-colors flex items-center gap-2"
                        >
                            {t('theme_config_cancel')}
                        </button>
                        <button
                            onClick={handleSave}
                            className="px-5 h-8.5 rounded-[10px] bg-neutral-first text-neutral-second text-sm font-semibold transition-colors shadow-lg flex items-center gap-2"
                        >
                            {t('theme_config_create')}
                        </button>
                    </div>
                </div>

                <div className="bg-neutral-second rounded-[10px] p-6">
                    <div className="space-y-6">
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
                            onDiscard={() => router.back()}
                            onDelete={() => { }}
                            onReset={() => { }}
                            isFactoryTheme={false}
                        />
                    </div>
                </div>
            </div>
        </>
    );
};

export default CreateThemePage;
