'use client';

import { useState, useRef } from 'react';
import { useRouter } from '@/i18n/navigation';
import { useParams } from 'next/navigation';

import { useIntakeForms } from '@/features/intake-form/hooks/useIntakeForms';
import { useRegister } from '@/context/RegisterContext';
import { useVCConfigs } from '@/features/register/hooks/useVCConfigs';
import { useClickOutside } from '@/shared/hooks';
import { useTranslations } from 'next-intl';
import dynamic from 'next/dynamic';
import ImportModal from '@/features/intake-form/components/ImportModal';
import { useImportFileConfigs } from '@/features/intake-form/hooks/useImportFileConfigs';

const VpVerificationModal = dynamic(
    () => import('@/features/verifiable-credentials/components/VpVerificationModal'),
    { ssr: false }
);

type Mechanism = {
    mechanism_id: string;
    mechanism_type: 'INTAKE_FORM' | 'IMPORT_FILE' | 'VERIFIABLE_CREDENTIAL';
    display_key: string;
};

type Props = {
    mechanisms?: any[];
    loading?: boolean;
};

export default function AddNewDropdown({
    mechanisms = [],
    loading = false
}: Props) {
    const router = useRouter();
    const params = useParams<{ type: string }>();
    const registerType = params.type;

    const t = useTranslations();

    const { currentRegister } = useRegister();
    const registerId = currentRegister?.register_id;

    const { forms, loading: formsLoading } = useIntakeForms(registerId);
    const { vcOptions, isLoadingVCs } = useVCConfigs();
    const { importFileOptions, isLoadingImportFiles } = useImportFileConfigs();

    const [open, setOpen] = useState(false);
    const [activeMenu, setActiveMenu] = useState<string | null>(null);
    const [showImportModal, setShowImportModal] = useState(false);

    const [selectedVC, setSelectedVC] = useState<any | null>(null);
    const [selectedImportFile, setSelectedImportFile] = useState<any | null>(null);
    const [openVC, setOpenVC] = useState(false);

    const ref = useRef<HTMLDivElement>(null);

    useClickOutside(ref, () => setOpen(false), open);

    const closeAll = () => {
        setOpen(false);
        setActiveMenu(null);
    };

    const handleNavigateForm = (formId: string) => {
        router.push(`/intake-form/${registerType}/new/${formId}`);
        closeAll();
    };

    const handleImport = (file: any) => {
        setSelectedImportFile(file);
        setShowImportModal(true);
        closeAll();
    };

    const handleVCSelect = (vc: any) => {
        setSelectedVC(vc);
        setOpenVC(true);
        closeAll();
    };

    const renderSubMenu = (mechanism: Mechanism) => {
        switch (mechanism.mechanism_type) {
            case 'INTAKE_FORM':
                if (formsLoading) {
                    return (
                        <div className="px-4 py-1 text-[16px] text-neutral-first/50">
                            {t('loading')}
                        </div>
                    );
                }

                if (!forms?.length) {
                    return (
                        <div className="px-4 py-1 text-[16px] text-neutral-first/50">
                            {t('no_options_available')}
                        </div>
                    );
                }

                return forms.map((form: any) => (
                    <div
                        key={form.form_id}
                        onClick={() => handleNavigateForm(form.form_id)}
                        className="px-4 py-1 font-medium hover:bg-secondary-second cursor-pointer truncate text-[16px]"
                        title={form.form_mnemonic}
                    >
                        {form.form_mnemonic}
                    </div>
                ));

            case 'IMPORT_FILE':
                if (isLoadingImportFiles) {
                    return (
                        <div className="px-4 py-1 text-[16px] text-neutral-first/50">
                            {t('loading')}
                        </div>
                    );
                }

                if (!importFileOptions?.length) {
                    return (
                        <div className="px-4 py-1 text-[16px] text-neutral-first/50">
                            {t('no_options_available')}
                        </div>
                    );
                }

                return importFileOptions.map((file: any) => (
                    <div
                        key={file.import_file_configuration_id}
                        onClick={() => handleImport(file)}
                        className="px-4 py-1 font-medium hover:bg-secondary-second cursor-pointer text-[16px] truncate"
                        title={file.import_file_template_mnemonic}
                    >
                        {file.import_file_template_mnemonic}
                    </div>
                ));

            case 'VERIFIABLE_CREDENTIAL':
                if (isLoadingVCs) {
                    return (
                        <div className="px-4 py-1 text-[16px] text-neutral-first/50">
                            {t('loading')}
                        </div>
                    );
                }

                if (!vcOptions?.length) {
                    return (
                        <div className="px-4 py-1 text-[16px] text-neutral-first/50">
                            {t('no_options_available')}
                        </div>
                    );
                }

                return vcOptions.map((vc: any) => (
                    <div
                        key={vc.vc_config_id}
                        onClick={() => handleVCSelect(vc)}
                        className="px-4 py-1 font-medium hover:bg-secondary-second cursor-pointer text-[16px] truncate"
                        title={`${vc.vc_mnemonic} - ${vc.data_model_mnemonic} - ${vc.intake_form_mnemonic}`}
                    >
                        {vc.vc_mnemonic} - {vc.data_model_mnemonic} - {vc.intake_form_mnemonic}
                    </div>
                ));

            default:
                return null;
        }
    };

    return (
        <>
            <div ref={ref} className="relative mt-2 w-full sm:w-100 max-w-full z-10">
                <button
                    onClick={() => {
                        setOpen(prev => {
                            if (prev) setActiveMenu(null);
                            return !prev;
                        });
                    }}
                    disabled={loading}
                    className={`w-full flex items-center justify-between gap-2.5 px-4 py-1 bg-neutral-second border border-primary-second rounded-[10px] truncate ${open ? 'border-b-transparent rounded-b-none' : ''}`}
                    title={t('new_intake')}
                >
                    <span
                        className={`text-[16px] font-medium truncate ${open ? 'text-neutral-first/50' : 'text-neutral-first'}`}
                    >
                        {t('new_intake')}
                    </span>

                    <img
                        src="/images/common/down_arrow.png"
                        alt="open"
                        width={14}
                        height={8}
                        className={`transition-transform ${open ? 'rotate-180' : ''}`}
                    />
                </button>

                {open && (
                    <div className="absolute left-0 top-full w-full bg-neutral-second border border-primary-second border-t-0 rounded-b-[10px] overflow-hidden z-50">
                        {loading ? (
                            <div className="px-4 py-1 text-[16px] text-neutral-first">
                                {t('loading')}
                            </div>
                        ) : !mechanisms.length ? (
                            <div className="px-4 py-1 text-[16px] text-neutral-first truncate">
                                {t('no_options_available')}
                            </div>
                        ) : (
                            mechanisms.map((mechanism, index) => (
                                <div key={mechanism.mechanism_id} className="w-full">
                                    <div className="px-4 py-1 text-neutral-first/50 font-medium">
                                        {mechanism.display_key}
                                    </div>

                                    <div className="text-neutral-first">
                                        {renderSubMenu(mechanism)}
                                    </div>

                                    {index !== mechanisms.length - 1 && (
                                        <div className="border-b border-primary-second" />
                                    )}
                                </div>
                            ))
                        )}
                    </div>
                )}
            </div>

            {openVC && selectedVC && (
                <VpVerificationModal
                    vc={selectedVC}
                    onClose={() => {
                        setOpenVC(false);
                        setSelectedVC(null);
                    }}
                />
            )}

            {showImportModal && (
                <ImportModal
                    onClose={() => setShowImportModal(false)}
                    importFileConfig={selectedImportFile}
                />
            )}
        </>
    );
}
