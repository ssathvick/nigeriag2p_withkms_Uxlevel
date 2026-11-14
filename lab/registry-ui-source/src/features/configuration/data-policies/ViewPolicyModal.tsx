'use client';

import { useTranslations } from 'next-intl';
import type { DataPolicy } from '@/features/configuration/shared/hooks/usePolicies';
import { BaseModal, Field } from '../shared/components';

interface ViewPolicyModalProps {
    onClose: () => void;
    data?: DataPolicy | null;
}

export default function ViewPolicyModal({ onClose, data }: ViewPolicyModalProps) {
    const t = useTranslations();

    if (!data) return null;

    return (
        <BaseModal
            title={t('view_policy')}
            onClose={onClose}
            maxWidth="max-w-220"
            secondaryActionLabel={t('close')}
        >
            <div className="bg-secondary-second/50 px-8 pt-2 pb-4">
                <Field label={t('policy_mnemonic')} value={data.policy_mnemonic} />
                <Field
                    label={t('policy_description')}
                    value={data.policy_description}
                    layout="column"
                />
                <Field label={t('policy_type')} value={data.policy_type} />
                <Field label={t('policy_id')} value={data.policy_id} />
                <Field label={t('register_id')} value={data.register_id} />
                <Field
                    label={t('policy_filter_expression')}
                    value={JSON.stringify(data.policy_filter_expression ?? {}, null, 2)}
                    layout="column"
                />
            </div>
        </BaseModal>
    );
}
