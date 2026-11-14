'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import Image from 'next/image';
import { toast } from 'react-toastify';
import { useFetch } from '@/shared/hooks';
import AddLanguageModal from './AddLanguageModal';
import EditLanguageModal from './EditLanguageModal';
import { Language } from '../types';
import { CONFIGURATION_REGISTRY_ACTIONS } from '../../shared/utils/configurationRegistry.actions';
import Can from '@/components/shared/Can';

interface LanguagesConfigViewProps {
    languages: Language[];
    setLanguages: React.Dispatch<React.SetStateAction<Language[]>>;
    loading: boolean;
    isModalOpen: boolean;
    onCloseModal: () => void;
    refetch: () => Promise<any>;
}

export default function LanguagesConfigView({
    languages,
    setLanguages,
    loading,
    isModalOpen,
    onCloseModal,
    refetch,
}: LanguagesConfigViewProps) {
    const t = useTranslations();
    const { execute: removeLanguage } = useFetch();
    const [editingLanguage, setEditingLanguage] = useState<Language | null>(null);

    const handleEdit = (lang: Language) => {
        setEditingLanguage(lang);
    };

    const handleDelete = async (lang: Language) => {
        if (lang.is_default) {
            toast.error(t('cannot_delete_default_language'));
            return;
        }

        toast.info(
            ({ closeToast }) => (
                <div className="p-1">
                    <p className="font-bold text-neutral-first mb-3">{t('confirm_delete_language', { label: lang.language_label })}</p>
                    <div className="flex gap-3">
                        <button
                            onClick={async () => {
                                closeToast();
                                try {
                                    const result = await removeLanguage('/api/configuration/registry/language/remove-language', {
                                        method: 'POST',
                                        body: JSON.stringify({ language_id: lang.language_id })
                                    });
                                    if (result) {
                                        toast.success(t('language_removed_success'));
                                        await refetch();
                                    }
                                } catch (error) {
                                    toast.error(t('error_occurred'));
                                }
                            }}
                            className="bg-primary-second text-neutral-second px-4 py-1.5 rounded-full text-sm font-semibold hover:bg-primary-second transition-colors shadow-sm"
                        >
                            {t('remove')}
                        </button>
                        <button
                            onClick={closeToast}
                            className="bg-secondary-first text-neutral-first/70 px-4 py-1.5 rounded-full text-sm font-semibold hover:bg-secondary-second transition-colors"
                        >
                            {t('cancel')}
                        </button>
                    </div>
                </div>
            ),
            {
                position: "top-right",
                autoClose: false,
                closeOnClick: false,
                draggable: false,
                closeButton: false,
                className: 'rounded-[15px] shadow-xl border border-secondary-first',
            }
        );
    };

    return (
        <>
            <div className="mx-7.5 bg-neutral-second rounded-[10px] p-4 pt-8 overflow-hidden shadow-sm">
                <div>
                    <div className="grid grid-cols-5 gap-4 pb-2 px-8 border-b border-secondary-first">
                        <div className="py-3 text-left text-base font-semibold text-primary-second tracking-wider">{t('flag')}</div>
                        <div className="py-3 text-left text-base font-semibold text-primary-second tracking-wider">{t('code')}</div>
                        <div className="py-3 text-left text-base font-semibold text-primary-second tracking-wider">{t('label')}</div>
                        <div className="py-3 text-left text-base font-semibold text-primary-second tracking-wider">{t('default')}</div>
                        <div className="py-3 text-left text-base font-semibold text-primary-second tracking-wider">{t('actions')}</div>
                    </div>

                    {loading ? (
                        <div className="flex justify-center items-center py-40">
                            <Image src="/images/common/loading.gif" alt="Loading" width={48} height={48} />
                        </div>
                    ) : languages.length === 0 ? (
                        <div className="py-20 text-center text-neutral-first/50 font-medium">
                            {t('no_languages_configured')}
                        </div>
                    ) : (
                        languages.map((lang, index) => (
                            <div key={lang.language_id} className="-mx-8">
                                <div
                                    className={`grid grid-cols-5 gap-4 items-center px-16 h-15 transition-colors ${index % 2 === 0 ? 'bg-secondary-second/25' : 'bg-neutral-second'
                                        } cursor-pointer`}
                                >
                                    <div className="flex items-center">
                                        <div className="w-10 h-6 relative rounded border overflow-hidden bg-secondary-first shadow-sm">
                                            {lang.language_flag_base64 ? (
                                                <Image src={lang.language_flag_base64} alt={lang.language_label} fill className="object-cover" />
                                            ) : (
                                                <div className="w-full h-full flex items-center justify-center text-[8px] opacity-30">No Flag</div>
                                            )}
                                        </div>
                                    </div>
                                    <div className="text-base font-medium truncate">{lang.language_code}</div>
                                    <div className="text-base font-medium truncate">{lang.language_label}</div>
                                    <div className="text-base font-medium">
                                        {lang.is_default == true ? 'True' : 'False'}
                                    </div>
                                    <div className="flex items-center gap-6">
                                        <Can action={CONFIGURATION_REGISTRY_ACTIONS.edit}>
                                            <button
                                                onClick={() => handleEdit(lang)}
                                                className="flex items-center hover:opacity-80 transition-opacity"
                                            >
                                                <span className="text-sm font-medium text-neutral-first/50">{t('common.edit')}</span>
                                                <Image src="/images/common/edit.png" alt="edit" width={18} height={18} className="ml-2 opacity-60" />
                                            </button>
                                            <button
                                                onClick={() => handleDelete(lang)}
                                                className="flex items-center hover:opacity-80 transition-opacity text-toast-failed-color"
                                            >
                                                <span className="text-sm font-medium text-neutral-first/50">{t('remove')}</span>
                                                <Image src="/images/common/false_sign.png" alt="remove" width={18} height={18} className="ml-2 opacity-60" />
                                            </button>
                                        </Can>
                                    </div>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>

            {isModalOpen && (
                <AddLanguageModal
                    isOpen={isModalOpen}
                    onClose={onCloseModal}
                    onSuccess={async (newLang) => {
                        if (newLang) {
                            await refetch();
                        }
                    }}
                />
            )}

            {editingLanguage && (
                <EditLanguageModal
                    isOpen={!!editingLanguage}
                    onClose={() => setEditingLanguage(null)}
                    onSuccess={async (updatedLang) => {
                        if (updatedLang) {
                            await refetch();
                        }
                    }}
                    language={editingLanguage}
                />
            )}
        </>
    );
}
