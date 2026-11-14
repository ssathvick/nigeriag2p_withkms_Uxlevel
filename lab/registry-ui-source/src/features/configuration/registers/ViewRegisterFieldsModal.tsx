'use client';

import Image from 'next/image';
import { useTranslations } from 'next-intl';
import { Register } from '../shared/types';
import { BaseModal, Field } from '../shared/components';

interface ViewRegisterFieldsModalProps {
    onClose: () => void;
    data?: Register;
}

export default function ViewRegisterFieldsModal({
    onClose,
    data,
}: ViewRegisterFieldsModalProps) {
    const t = useTranslations();

    if (!data) return null;

    return (
        <BaseModal
            title={`${data.register_mnemonic} ${t('details')}`}
            onClose={onClose}
            secondaryActionLabel={t('close')}
            maxWidth="max-w-200"
        >
            <div className="bg-secondary-second/50 px-8 pt-2 pb-4">
                <Field label={t('registry_name')} value={data.register_mnemonic} />
                <Field label={t('register_subject')} value={data.register_subject} />
                <Field label={t('description')} value={data.register_description} />
                <Field label={t('register_purpose')} value={data.register_purpose || '-'} />
                <Field
                    label={t('master_register')}
                    value={data.master_register_mnemonic || data.master_register_id}
                />
                <Field
                    label={t('deduplication_enabled')}
                    value={data.dedup_is_enabled ? t('true') : t('false')}
                />
                <Field label={t('dedup_threshold_score')} value={data.dedup_threshold_score ?? 0} />
                <Field
                    label={t('functional_id_generation_required')}
                    value={data.functional_id_generation_required ? t('true') : t('false')}
                />
                <Field
                    label={t('completion_score_required')}
                    value={data.completion_score_required ? t('true') : t('false')}
                />
                <Field label={t('register_rank')} value={data.register_rank ?? 0} />
                <Field label={t('program_id')} value={data.program_id} />
                <Field label={t('has_image')} value={data.has_image ? t('true') : t('false')} />
                <Field label={t('has_data')} value={data.has_data ? t('true') : t('false')} />
                <Field
                    label={t('register_icon')}
                    value={data.register_icon ? (
                        <div className="w-20 h-20 bg-secondary-first border border-secondary-first rounded-2xl overflow-hidden shadow-inner flex items-center justify-center p-2">
                            <Image
                                src={data.register_icon.startsWith('data:') ? data.register_icon : `data:image/png;base64,${data.register_icon}`}
                                alt={t('register_logo_alt')}
                                width={120}
                                height={120}
                                className="object-contain"
                                unoptimized
                            />
                        </div>
                    ) : (
                        <span className="text-neutral-first/50 italic text-sm">{t('no_icon_uploaded')}</span>
                    )}
                />
            </div>
        </BaseModal>
    );
}
