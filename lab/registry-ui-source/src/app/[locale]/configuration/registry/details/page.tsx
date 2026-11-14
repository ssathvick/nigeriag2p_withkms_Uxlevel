'use client';

import { useState } from 'react';
import { TopBar } from '@/components/shared';
import Image from 'next/image';
import { useFetch } from '@/shared/hooks/useFetch';
import { convertImageToBase64 } from '@/features/configuration/shared';
import { toast } from 'react-toastify';
import Can from '@/components/shared/Can';
import { CONFIGURATION_REGISTRY_ACTIONS } from '@/features/configuration/shared/utils/configurationRegistry.actions';
import { useTranslations } from 'next-intl';
import { useTheme } from '@/features/configuration/registry/hooks/useTheme';
import { useLang } from '@/features/configuration/registry/hooks/useLang';
import EditRegistry from '@/features/configuration/registry/components/EditRegistry';
import { useRouter, usePathname } from '@/i18n/navigation';

const RegistryConfigurationPage = () => {
	const t = useTranslations();
	const router = useRouter();
	const pathname = usePathname();
	const { themes, themesLoading } = useTheme();
	const { languages, languagesLoading } = useLang();
	const [isEditing, setIsEditing] = useState(false);
	const [configurationId, setConfigurationId] = useState<string | null>(null);
	const [registryName, setRegistryName] = useState(t('registry_name'));
	const [image, setImage] = useState('/images/config/blank_image.png');
	const [themeId, setThemeId] = useState<string | null>(null);
	const [languageId, setLanguageId] = useState<string | null>(null);

	const { data: registryData } = useFetch({ url: '/api/configuration/registry/get' });
	const { execute: saveRegistry } = useFetch();


	// Update local state when we enter edit mode
	const startEditing = () => {
		if (registryData) {
			setConfigurationId(registryData.configuration_id);
			setRegistryName(registryData.registry_name || t('registry_name'));
			setImage(registryData.registry_logo || '/images/config/blank_image.png');
			setThemeId(registryData.registry_theme_id || null);
			setLanguageId(registryData.registry_language_id || null);
		}
		setIsEditing(true);
	};

	const handleSave = async (newName: string, newImage: string, newThemeId: string | null, newLanguageId: string | null) => {
		const base64Logo = await convertImageToBase64(newImage);

		const endpoint = configurationId || registryData?.configuration_id
			? '/api/configuration/registry/update'
			: '/api/configuration/registry/create';

		const payload = configurationId || registryData?.configuration_id
			? {
				configuration_id: configurationId || registryData?.configuration_id,
				registry_name: newName,
				registry_logo: base64Logo,
				registry_theme_id: newThemeId,
				registry_language_id: newLanguageId
			}
			: {
				registry_name: newName,
				registry_logo: base64Logo,
				registry_theme_id: newThemeId,
				registry_language_id: newLanguageId
			};

		const result = await saveRegistry(endpoint, {
			method: 'POST',
			body: JSON.stringify(payload)
		});

		if (result?.configuration_id) {
			setConfigurationId(result.configuration_id);
			setRegistryName(newName);
			setImage(newImage);
			setThemeId(newThemeId);
			setLanguageId(newLanguageId);
			setIsEditing(false);
			toast.success(t('toast_registry_config_saved'));

			const newLangObj = languages.find(l => l.language_id === newLanguageId);
			if (newLangObj && newLangObj.language_code) {
				router.replace(pathname, { locale: newLangObj.language_code });
				router.refresh();
			} else {
				window.location.reload();
			}
		} else {
			toast.error(t('toast_registry_config_save_failed'));
		}
	};

	return (
		<>
			<TopBar
				breadcrumb={[{ label: t('registry') }]}
				showFilters={false}
				showPagination={false}
				showAddNewButton={false}
			/>

			<div className="mx-7.5">
				<div className="w-full max-w-xl">
					{isEditing ? (
						<EditRegistry
							initialName={registryName}
							initialImage={image}
							initialThemeId={registryData?.registry_theme_id || themeId}
							initialLanguageId={registryData?.registry_language_id || languageId}
							themes={themes}
							themesLoading={themesLoading}
							languages={languages}
							languagesLoading={languagesLoading}
							onSave={handleSave}
							onCancel={() => setIsEditing(false)}
						/>
					) : (
						<div className="bg-neutral-second rounded-[10px] p-12">
							<div className="flex flex-col gap-8">
								<div className='flex flex-col items-start gap-3'>
									<span className='text-neutral-first text-[16px] font-normal tracking-normal m-0 opacity-60'>{t('registry_logo')}</span>
									<div className="w-25 h-25 relative shrink-0 rounded overflow-hidden flex items-center justify-center border border-secondary-second/30 p-2">
										<Image
											src={registryData?.registry_logo || image}
											alt={t('registry_logo_alt')}
											width={100}
											height={100}
											className="object-contain w-full h-full"
											unoptimized
										/>
									</div>
								</div>

								<div className='flex flex-col items-start gap-2'>
									<span className='text-neutral-first text-[16px] font-normal tracking-normal m-0 opacity-60'>{t('registry_name')}</span>
									<span className="text-primary-second text-xl m-0 font-semibold">
										{registryData?.registry_name || registryName}
									</span>
								</div>

								<div className='flex flex-col items-start gap-2'>
									<span className='text-neutral-first text-[16px] font-normal tracking-normal m-0 opacity-60'>{t('registry_theme')}</span>
									<span className="text-primary-second text-xl m-0 font-semibold capitalize">
										{themes.find(th => th.theme_id === (registryData?.registry_theme_id || themeId))?.theme_mnemonic || ''}
									</span>
								</div>

								<div className='flex flex-col items-start gap-2'>
									<span className='text-neutral-first text-[16px] font-normal tracking-normal m-0 opacity-60'>{t('registry_language')}</span>
									<span className="text-primary-second text-xl m-0 font-semibold capitalize">
										{languages.find(l => l.language_id === (registryData?.registry_language_id || languageId))?.language_label || ''}
									</span>
								</div>

								<Can action={CONFIGURATION_REGISTRY_ACTIONS.edit}>
									<div className="pt-4">
										<button
											onClick={startEditing}
											className='h-9 px-6 bg-neutral-first text-neutral-second rounded-[10px] flex items-center justify-center cursor-pointer hover:bg-neutral-first/90 transition-all active:scale-95 text-sm font-semibold'
										>
											{t('common.edit')}
										</button>
									</div>
								</Can>
							</div>
						</div>
					)}
				</div>
			</div>
		</>
	);
};

export default RegistryConfigurationPage;
