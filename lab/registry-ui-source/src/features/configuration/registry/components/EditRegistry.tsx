'use client';

import Image from 'next/image';
import { useState } from 'react';
import { Upload, Trash2, Image as ImageIcon } from 'lucide-react';
import { useTranslations } from 'next-intl';
import ImageCropper from '@/components/shared/ImageCropper';
import ThemeSelector from './ThemeSelector';
import LanguageSelector from './LanguageSelector';
import { Theme, Language } from '../types';

interface EditRegistryProps {
    initialName: string;
    initialImage: string;
    initialThemeId: string | null;
    initialLanguageId: string | null;
    themes: Theme[];
    themesLoading: boolean;
    languages: Language[];
    languagesLoading: boolean;
    onSave: (name: string, image: string, themeId: string | null, languageId: string | null) => void;
    onCancel: () => void;
}

export default function EditRegistry({
    initialName,
    initialImage,
    initialThemeId,
    initialLanguageId,
    themes,
    themesLoading,
    languages,
    languagesLoading,
    onSave,
    onCancel,
}: EditRegistryProps) {
    const t = useTranslations();
    const [name, setName] = useState(initialName);
    const [image, setImage] = useState(initialImage);
    const [selectedThemeId, setSelectedThemeId] = useState<string | null>(initialThemeId);
    const [selectedLanguageId, setSelectedLanguageId] = useState<string | null>(initialLanguageId);
    const [croppingImage, setCroppingImage] = useState<string | null>(null);
    const [isCropperOpen, setIsCropperOpen] = useState(false);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            const reader = new FileReader();
            reader.onloadend = () => {
                setCroppingImage(reader.result as string);
                setIsCropperOpen(true);
            };
            reader.readAsDataURL(file);
        }
    };

    const handleCropComplete = (croppedImage: string) => {
        setImage(croppedImage);
        setIsCropperOpen(false);
        setCroppingImage(null);
    };

    const handleCropCancel = () => {
        setIsCropperOpen(false);
        setCroppingImage(null);
    };

    const triggerUpload = () => {
        document.getElementById('registry-image-upload')?.click();
    };

    return (
        <>
            <div className="bg-primary-first/20 rounded-[10px] p-8 border-2 border-dashed border-primary-second w-full flex flex-col font-roboto">
                <div className="flex flex-col gap-10">
                    {/* Logo Section */}
                    <div className='flex flex-col items-start gap-3'>
                        <span className='text-neutral-first text-[16px] font-normal tracking-normal m-0 opacity-60'>{t('registry_logo')}</span>
                        <div className="relative group w-30 h-30 bg-secondary-second rounded-[10px] flex items-center justify-center overflow-hidden shrink-0 border border-secondary-second/30">
                            <input
                                type="file"
                                id="registry-image-upload"
                                className="hidden"
                                accept="image/*"
                                onChange={handleFileChange}
                            />
                            {image && image !== '/images/config/blank_image.png' ? (
                                <Image
                                    src={image}
                                    alt={t('register_logo_alt')}
                                    width={120}
                                    height={120}
                                    className="object-contain"
                                    unoptimized
                                />
                            ) : (
                                <div className="flex flex-col items-center justify-center text-secondary-third">
                                    <ImageIcon size={50} strokeWidth={1} />
                                </div>
                            )}

                            {/* Overlay Action Buttons */}
                            <div className="absolute inset-0 bg-neutral-first/40 flex flex-col items-center justify-center gap-3 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                                <button
                                    onClick={triggerUpload}
                                    className="flex items-center justify-center gap-2 w-23.75 py-1.5 bg-neutral-second rounded-[10px] text-primary-second shadow-md hover:bg-secondary-first transition-all active:scale-95"
                                >
                                    <Upload size={15} strokeWidth={2.5} />
                                    <span className="text-[13px] leading-none">{t('upload')}</span>
                                </button>
                                <button
                                    onClick={() => setImage('/images/config/blank_image.png')}
                                    className="flex items-center justify-center gap-2 w-23.75 py-1.5 bg-neutral-second rounded-[10px] text-primary-second shadow-md hover:bg-secondary-first transition-all active:scale-95"
                                >
                                    <Trash2 size={15} strokeWidth={2.5} />
                                    <span className="text-[13px] leading-none">{t('remove')}</span>
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Input Area */}
                    <div className="flex flex-col gap-6 w-full max-w-md pb-6">
                        <div className='flex flex-col items-start gap-2 w-full'>
                            <span className='text-neutral-first text-[16px] font-normal tracking-normal m-0 opacity-60'>{t('registry_name')}</span>
                            <input
                                type="text"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                placeholder={t('registry_name')}
                                className="w-full h-10 px-4 rounded-[10px] border border-primary-second text-[16px] font-medium text-neutral-first bg-neutral-second outline-none placeholder:text-neutral-first/50"
                            />
                        </div>

                        <div className="flex flex-col items-start gap-2 w-full">
                            <span className='text-neutral-first text-[16px] font-normal tracking-normal m-0 opacity-60'>{t('registry_theme')}</span>
                            <ThemeSelector
                                themes={themes}
                                themesLoading={themesLoading}
                                selectedThemeId={selectedThemeId}
                                onSelectTheme={setSelectedThemeId}
                            />
                        </div>

                        <div className="flex flex-col items-start gap-2 w-full">
                            <span className='text-neutral-first text-[16px] font-normal tracking-normal m-0 opacity-60'>{t('registry_language')}</span>
                            <LanguageSelector
                                languages={languages}
                                languagesLoading={languagesLoading}
                                selectedLanguageId={selectedLanguageId}
                                onSelectLanguage={setSelectedLanguageId}
                            />
                        </div>
                    </div>
                </div>

                {/* Divider and Bottom Section */}
                <div className="space-y-6">
                    {/* Divider */}
                    <div className="w-full h-px bg-primary-first" />

                    {/* Buttons Row */}
                    <div className="flex gap-3">
                        <button
                            onClick={onCancel}
                            className="h-8.5 px-6 rounded-[10px] bg-neutral-first text-neutral-second text-sm font-semibold transition-all active:scale-95"
                        >
                            {t('cancel')}
                        </button>
                        <button
                            onClick={() => onSave(name, image, selectedThemeId, selectedLanguageId)}
                            className="h-8.5 px-6 rounded-[10px] bg-neutral-first text-neutral-second text-sm font-semibold transition-all active:scale-95"
                        >
                            {t('save')}
                        </button>
                    </div>
                </div>
            </div>

            {isCropperOpen && croppingImage && (
                <ImageCropper
                    image={croppingImage}
                    onCropComplete={handleCropComplete}
                    onCancel={handleCropCancel}
                />
            )}
        </>
    );
}
