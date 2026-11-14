'use client';

import { useTranslations } from 'next-intl';
import { BaseModal, Field } from '../shared/components';

interface ViewIntakeFormModalProps {
    onClose: () => void;
    data?: any;
}

export default function ViewIntakeFormModal({
    onClose,
    data,
}: ViewIntakeFormModalProps) {
    const t = useTranslations();

    return (
        <BaseModal
            title={t('view_intake_form')}
            onClose={onClose}
            maxWidth="max-w-220"
            secondaryActionLabel={t('close')}
        >
            <div className="bg-secondary-second/50 px-8 pt-2 pb-4">
                {/* <Field label={t('form_id')} value={data?.form_id} /> */}
                <Field label={t('form_mnemonic')} value={data?.form_mnemonic} />
                {/* <Field label={t('register_id')} value={data?.register_id} /> */}
                <Field label={t('register_mnemonic')} value={data?.register_mnemonic} />
                <Field
                    label={t('number_of_verifications')}
                    value={data?.number_of_verifications}
                />

                <div className="pt-4">
                    <span className="text-secondary-third text-[16px] font-medium block mb-2">
                        {t('description')}
                    </span>
                    <div className="text-neutral-first text-[16px] font-normal bg-neutral-second p-4 rounded-lg border border-secondary-first">
                        {data?.form_description || '-'}
                    </div>
                </div>
            </div>
        </BaseModal>
    );
}
