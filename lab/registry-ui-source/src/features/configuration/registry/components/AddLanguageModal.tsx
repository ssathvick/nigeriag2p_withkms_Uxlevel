'use client';

import { useState, useRef, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { toast } from 'react-toastify';
import Image from 'next/image';
import { Upload, Download } from 'lucide-react';
import { readAndValidateJson } from '../utils/language.helpers';
import { useFetch } from '@/shared/hooks';
import { BaseModal, InputField, CheckboxField } from '../../shared/components';

interface AddLanguageModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess?: (data: any) => void;
}

export default function AddLanguageModal({
    isOpen,
    onClose,
    onSuccess
}: AddLanguageModalProps) {
    const t = useTranslations();
    const { execute: saveLanguage } = useFetch();

    const [language_code, setLanguageCode] = useState('');
    const [language_label, setLanguageLabel] = useState('');
    const [isDefault, setIsDefault] = useState(false);
    const [language_flag_base64, setLanguageFlagBase64] = useState('');
    const [flagFileName, setFlagFileName] = useState('');
    const [language_translation, setLanguageTranslation] = useState<any>(null);
    const [fileName, setFileName] = useState('');
    const [loading, setLoading] = useState(false);

    const fileInputRef = useRef<HTMLInputElement>(null);
    const flagInputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        if (isOpen) {
            setLanguageCode('');
            setLanguageLabel('');
            setIsDefault(false);
            setLanguageFlagBase64('');
            setLanguageTranslation(null);
            setFileName('');
        }
    }, [isOpen]);

    if (!isOpen) return null;

    const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        try {
            const json = await readAndValidateJson(file);
            setLanguageTranslation(json);
            setFileName(file.name);
        } catch (error: any) {
            toast.error(error.message);
            if (fileInputRef.current) fileInputRef.current.value = '';
        }
    };

    const handleFlagChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setFlagFileName(file.name);
        const reader = new FileReader();
        reader.onload = (event) => {
            setLanguageFlagBase64(event.target?.result as string);
        };
        reader.readAsDataURL(file);
    };

    const handleDownloadJson = () => {
        if (!language_translation) return;
        const blob = new Blob([JSON.stringify(language_translation, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${language_code || 'locale'}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    const handleSave = async () => {
        if (!language_code || !language_label || !language_translation) {
            toast.warn(t('fill_required_fields'));
            return;
        }

        setLoading(true);
        const payload = {
            language_code,
            language_label,
            language_flag_base64,
            is_default: isDefault,
            language_translation
        };

        try {
            const result = await saveLanguage('/api/configuration/registry/language/create-language', {
                method: 'POST',
                body: JSON.stringify(payload)
            });

            if (result) {
                toast.success(t('language_created_success'));
                if (onSuccess) onSuccess(result);
                onClose();
            } else {
                toast.error(t('save_failed'));
            }
        } catch (error) {
            toast.error(t('error_occurred'));
        } finally {
            setLoading(false);
        }
    };

    return (
        <BaseModal
            title={t('add_new_language')}
            onClose={onClose}
            primaryActionLabel={t('save')}
            onPrimaryAction={handleSave}
            maxWidth='max-w-3xl'
        >
            <div className="flex flex-col gap-6 w-full">
                <div className="grid grid-cols-2 gap-4">
                    <InputField
                        label={t('language_code')}
                        value={language_code}
                        onChange={setLanguageCode}
                        placeholder={t('language_code_placeholder')}
                    />
                    <InputField
                        label={t('language_label')}
                        value={language_label}
                        onChange={setLanguageLabel}
                        placeholder={t('language_label_placeholder')}
                    />
                </div>

                <div className="flex flex-col gap-2">
                    <label className="text-sm font-semibold text-neutral-first/60">{t('language_flag')}</label>
                    <div className="flex items-center gap-4">
                        <div className="w-1/2 h-10 px-4 rounded-[10px] border border-neutral-first/10 bg-neutral-first/5 flex items-center overflow-hidden">
                            {language_flag_base64 ? (
                                <div className="flex items-center gap-2 overflow-hidden">
                                    <div className="w-8 h-5 relative rounded border overflow-hidden shrink-0">
                                        <Image src={language_flag_base64} alt="flag" fill className="object-cover" />
                                    </div>
                                    <span className="text-sm text-neutral-first/60 truncate">
                                        {flagFileName || t('flag_image')}
                                    </span>
                                </div>
                            ) : (
                                <span className="text-sm text-neutral-first/40">{t('no_file_selected')}</span>
                            )}
                        </div>
                        <button
                            type="button"
                            onClick={() => flagInputRef.current?.click()}
                            className="h-10 px-4 rounded-[10px] border border-primary-second text-primary-second text-sm font-bold hover:bg-primary-second/5 transition-colors flex items-center gap-2"
                        >
                            <Upload size={18} />
                            {t('upload_flag')}
                        </button>
                        <input
                            type="file"
                            ref={flagInputRef}
                            onChange={handleFlagChange}
                            className="hidden"
                            accept="image/*"
                        />
                    </div>
                </div>

                <div className="flex flex-col gap-2">
                    <label className="text-sm font-semibold text-neutral-first/60">{t('translation_file')} (.json)</label>
                    <div className="flex items-center gap-4">
                        <div className="w-1/2 h-10 px-4 rounded-[10px] border border-neutral-first/10 bg-neutral-first/5 flex items-center overflow-hidden">
                            <span className="text-sm text-neutral-first/60 truncate">
                                {fileName || t('no_file_selected')}
                            </span>
                        </div>
                        <button
                            type="button"
                            onClick={handleDownloadJson}
                            disabled={!language_translation}
                            className="h-10 px-4 rounded-[10px] border border-primary-second text-primary-second text-sm font-bold hover:bg-primary-second/5 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            <Download size={18} />
                            {t('download')}
                        </button>
                        <button
                            type="button"
                            onClick={() => fileInputRef.current?.click()}
                            className="h-10 px-4 rounded-[10px] border border-primary-second text-primary-second text-sm font-bold hover:bg-primary-second/5 transition-colors flex items-center gap-2"
                        >
                            <Upload size={18} />
                            {t('upload')}
                        </button>
                        <input
                            type="file"
                            ref={fileInputRef}
                            onChange={handleFileChange}
                            className="hidden"
                            accept=".json"
                        />
                    </div>
                </div>

                <CheckboxField
                    label={t('set_as_default_language')}
                    checked={isDefault}
                    onChange={setIsDefault}
                />
            </div>
        </BaseModal>
    );
}
