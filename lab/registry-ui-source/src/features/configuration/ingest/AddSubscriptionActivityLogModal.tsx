'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { useFetch } from '@/shared/hooks';
import { toast } from 'react-toastify';
import { BaseModal, CustomDropdown, InputField, TextAreaField } from '../shared/components';

interface AddSubscriptionActivityLogModalProps {
    onClose: () => void;
    onSuccess?: () => void;
}

export default function AddSubscriptionActivityLogModal({ onClose, onSuccess }: AddSubscriptionActivityLogModalProps) {
    const t = useTranslations();
    const { execute: createLog } = useFetch();

    const [formData, setFormData] = useState({
        partner_id: '',
        is_unsubscribe: false,
        description: '',
        subscription_url: '',
        registry_callback_url: '',
        header: '{}',
        payload: '{}',
        response: '{}',
    });

    const resetForm = () => {
        setFormData({
            partner_id: '',
            is_unsubscribe: false,
            description: '',
            subscription_url: '',
            registry_callback_url: '',
            header: '{}',
            payload: '{}',
            response: '{}',
        });
    };

    const handleCancel = () => {
        resetForm();
        onClose();
    };

    const handleSubmit = async () => {
        if (!formData.partner_id) {
            toast.warn(t('partner_id') + ' is required');
            return;
        }

        try {
            const result = await createLog('/api/configuration/ingest/create-subscription-activity-log', {
                method: 'POST',
                body: JSON.stringify({
                    partner_id: formData.partner_id,
                    is_unsubscribe: formData.is_unsubscribe,
                    description: formData.description || null,
                    subscription_url: formData.subscription_url || null,
                    registry_callback_url: formData.registry_callback_url || null,
                    header: JSON.parse(formData.header),
                    payload: JSON.parse(formData.payload),
                    response: JSON.parse(formData.response),
                })
            });

            if (result?.subscription_activity_log_id) {
                toast.success(t('toast_subscription_log_created'));
                resetForm();
                if (onSuccess) onSuccess();
                onClose();
            } else {
                toast.error(t('toast_subscription_log_create_failed'));
            }
        } catch (e) {
            toast.error(t('invalid_json_format'));
        }
    };

    return (
        <BaseModal
            title={t('add_subscription_log')}
            onClose={handleCancel}
            primaryActionLabel={t('save')}
            onPrimaryAction={handleSubmit}
            maxWidth="max-w-3xl"
        >
            <div className="space-y-6">
                <InputField
                    label={t('partner_id')}
                    value={formData.partner_id}
                    onChange={(value) => setFormData({ ...formData, partner_id: value })}
                />

                <CustomDropdown
                    label={t('unsubscribe')}
                    value={formData.is_unsubscribe ? 'true' : 'false'}
                    options={[
                        { label: t('true'), value: 'true' },
                        { label: t('false'), value: 'false' },
                    ]}
                    onChange={(value) => setFormData({ ...formData, is_unsubscribe: value === 'true' })}
                />

                <InputField
                    label={t('subscription_url')}
                    value={formData.subscription_url}
                    onChange={(value) => setFormData({ ...formData, subscription_url: value })}
                />

                <InputField
                    label={t('callback_url')}
                    value={formData.registry_callback_url}
                    onChange={(value) => setFormData({ ...formData, registry_callback_url: value })}
                />

                <TextAreaField
                    label={t('description')}
                    value={formData.description}
                    onChange={(value) => setFormData({ ...formData, description: value })}
                    rows={2}
                />

                <TextAreaField
                    label={t('header') + ' (JSON)'}
                    value={formData.header}
                    onChange={(value) => setFormData({ ...formData, header: value })}
                    rows={8}
                    textareaClassName="font-mono text-xs"
                />

                <TextAreaField
                    label={t('payload') + ' (JSON)'}
                    value={formData.payload}
                    onChange={(value) => setFormData({ ...formData, payload: value })}
                    rows={18}
                    textareaClassName="font-mono text-xs"
                />

                <TextAreaField
                    label={t('response') + ' (JSON)'}
                    value={formData.response}
                    onChange={(value) => setFormData({ ...formData, response: value })}
                    rows={22}
                    textareaClassName="font-mono text-xs"

                />
            </div>
        </BaseModal>
    );
}
