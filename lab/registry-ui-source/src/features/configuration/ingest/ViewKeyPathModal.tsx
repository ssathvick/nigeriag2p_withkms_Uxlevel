'use client';

import { useTranslations } from 'next-intl';
import { IncomingKeyPath } from '@/features/configuration/shared/hooks/useAllIncomingKeyPaths';
import { BaseModal, Field } from '../shared/components';

interface ViewKeyPathModalProps {
    onClose: () => void;
    data?: IncomingKeyPath;
}

export default function ViewKeyPathModal({
    onClose,
    data,
}: ViewKeyPathModalProps) {
    const t = useTranslations();

    return (
        <BaseModal
            title={`${t('view_ingest_key_path')}`}
            onClose={onClose}
            maxWidth='max-w-220'
            secondaryActionLabel={t('close')}
        >
            <div className="bg-secondary-second/50 px-8 pt-2 pb-4">
                <Field label={t('data_model')} value={data?.data_model_mnemonic} />

                <Field
                    label={t('key_path_for_message_id')}
                    value={data?.key_path_for_message_id}
                    layout="column"
                />

                <Field
                    label={t('key_path_for_sender')}
                    value={data?.key_path_for_sender}
                    layout="column"
                />

                <Field
                    label={t('key_path_for_signature')}
                    value={data?.key_path_for_signature}
                    layout="column"
                />

                <Field
                    label={t('key_path_for_signature_payload')}
                    value={data?.key_path_for_signature_payload}
                    layout="column"
                />

                <Field label={t('is_list')} value={data?.is_list ? t('true') : t('false')} />

                {data?.is_list && (
                    <Field
                        label={t('key_path_for_list_elements')}
                        value={data?.key_path_for_list_elements}
                        layout="column"
                    />
                )}
            </div>
        </BaseModal>
    );
}
