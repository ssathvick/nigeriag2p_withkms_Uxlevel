'use client';

import { useTranslations } from 'next-intl';
import { IncomingSemanticPattern } from '@/features/configuration/shared/hooks/useAllSemanticPatterns';
import { BaseModal, Field } from '../shared/components';


interface ViewSemanticPatternModalProps {
    onClose: () => void;
    data?: IncomingSemanticPattern;
}

export default function ViewSemanticPatternModal({
    onClose,
    data,
}: ViewSemanticPatternModalProps) {
    const t = useTranslations();

    return (
        <BaseModal
            title={t("view_semantic_pattern")}
            onClose={onClose}
            maxWidth='max-w-220'
            secondaryActionLabel={t('close')}
        >
            <div className="bg-secondary-second/50 px-8 pt-2 pb-4">
                <Field label={t('data_model')} value={data?.data_model_mnemonic} />

                <Field label={t('register')} value={data?.register_mnemonic} />

                <Field label={t('intake_form_mnemonic')} value={data?.intake_form_mnemonic} />

                <Field
                    label={t('pattern_for_register')}
                    value={data?.pattern_for_register}
                    layout="column"
                />

                <Field
                    label={t('pattern_for_intake_form')}
                    value={data?.pattern_for_intake_form}
                    layout="column"
                />

                <Field
                    label={t('key_path_for_business_payload')}
                    value={data?.key_path_for_business_payload}
                    layout="column"
                />

                <Field
                    label={t('raw_payload_enricher_class')}
                    value={data?.raw_payload_enricher_class}
                    layout="column"
                />
            </div>
        </BaseModal>
    );
}
