'use client';

import { useTranslations } from 'next-intl';
import { BaseModal, Field } from '../shared/components';

interface Props {
    onClose: () => void;
    data?: any;
}

export default function ViewDataModelModal({
    onClose,
    data,
}: Props) {
    const t = useTranslations();

    return (
        <BaseModal
            title={t('view_data_model')}
            onClose={onClose}
            maxWidth='max-w-200'
        >
            <div className="bg-secondary-second/50 px-8 pt-2 pb-4">
                <Field label={t('data_model_mnemonic')} value={data?.data_model_mnemonic} />

                <Field label={t('template_id')} value={data?.response_template_file_id} />

                <Field
                    label={t('status')}
                    value={data?.is_active ? t('active') : t('inactive')}
                />

                <Field label={t('pattern')} value={data?.pattern_for_data_model} />
            </div>
        </BaseModal>
    );
}
