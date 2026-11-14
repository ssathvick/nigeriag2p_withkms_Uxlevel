'use client';

import { useTranslations } from 'next-intl';
import { BaseModal, Field } from '../shared/components';

interface ViewIntakeFormTabSectionModalProps {
    onClose: () => void;
    data?: any;
}

export default function ViewIntakeFormTabSectionModal({
    onClose,
    data,
}: ViewIntakeFormTabSectionModalProps) {
    const t = useTranslations();

    return (
        <BaseModal
            title={t('view_intake_form_tab_section')}
            onClose={onClose}
            maxWidth="max-w-220"
            secondaryActionLabel={t('close')}
        >
            <div className="bg-secondary-second/50 px-8 pt-2 pb-4">
                <Field label={t('section_id')} value={data?.section_id} />
                <Field label={t('section_order')} value={data?.section_order} />
                <Field label={t('section_mnemonic')} value={data?.section_mnemonic} />
            </div>
        </BaseModal>
    );
}
