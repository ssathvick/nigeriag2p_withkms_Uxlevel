'use client';

import { useTranslations } from 'next-intl';
import { BaseModal, Field } from '../shared/components';

interface ViewIntakeFormTabModalProps {
    onClose: () => void;
    data?: any;
}

export default function ViewIntakeFormTabModal({
    onClose,
    data,
}: ViewIntakeFormTabModalProps) {
    const t = useTranslations();

    return (
        <BaseModal
            title={t('view_intake_form_tab')}
            onClose={onClose}
            maxWidth="max-w-220"
            secondaryActionLabel={t('close')}
        >
            <div className="bg-secondary-second/50 px-8 pt-2 pb-4">
                <Field label={t('tab_label')} value={data?.tab_label} />
                <Field label={t('tab_order')} value={data?.tab_order} />
            </div>
        </BaseModal>
    );
}
