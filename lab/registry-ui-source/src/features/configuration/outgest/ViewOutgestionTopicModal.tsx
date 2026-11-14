'use client';

import { useTranslations } from 'next-intl';
import { BaseModal, Field } from '../shared/components';
import { formatDateTime } from '@/shared/utils/dateUtils';


interface Props {
    onClose: () => void;
    data?: any;
}

export default function ViewOutgestionTopicModal({
    onClose,
    data,
}: Props) {
    const t = useTranslations();

    return (
        <BaseModal
            title={t('view_outgestion_topic')}
            onClose={onClose}
            maxWidth="max-w-200"
        >
            <div className="bg-secondary-second/50 px-8 pt-2 pb-4">
                <Field label={t('register_mnemonic')} value={data?.register_mnemonic} />

                <Field label={t('data_model_mnemonic')} value={data?.data_model_mnemonic} />

                <Field label={t('websub_topic')} value={data?.websub_topic} />

                <Field label={t('description')} value={data?.description} />

                <Field
                    label={t('is_active')}
                    value={data?.is_active ? t('true') : t('false')}
                />

                <Field
                    label={t('websub_register_status')}
                    value={data?.websub_register_status}
                />

                <Field
                    label={t('websub_register_datetime')}
                    value={formatDateTime(data?.websub_register_datetime)}
                />

                <Field
                    label={t('websub_register_attempts')}
                    value={data?.websub_register_number_of_attempts}
                />

                <Field
                    label={t('websub_register_error')}
                    value={data?.websub_register_latest_error_message}
                />
            </div>
        </BaseModal>
    );
}
