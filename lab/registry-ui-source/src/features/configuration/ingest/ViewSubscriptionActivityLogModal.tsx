'use client';

import { useTranslations } from 'next-intl';
import { SubscriptionActivityLog } from '@/features/configuration/shared/hooks/useAllSubscriptionActivityLogs';
import { BaseModal, Field } from '../shared/components';

interface ViewSubscriptionActivityLogModalProps {
    onClose: () => void;
    data?: SubscriptionActivityLog;
}

export default function ViewSubscriptionActivityLogModal({
    onClose,
    data,
}: ViewSubscriptionActivityLogModalProps) {
    const t = useTranslations();

    const renderJSON = (obj: any) => {
        try {
            return (
                <div className="bg-secondary-first p-4 rounded-lg border border-secondary-first mt-2 overflow-x-auto">
                    <pre className="text-xs font-mono text-neutral-first">
                        {JSON.stringify(obj, null, 2)}
                    </pre>
                </div>
            );
        } catch (e) {
            return <span className="text-secondary-third italic">Invalid JSON</span>;
        }
    };

    return (
        <BaseModal
            title={t('view_subscription_activity_log')}
            onClose={onClose}
            maxWidth="max-w-4xl"
            secondaryActionLabel={t('close')}
        >
            <div className="bg-secondary-first rounded-[10px] p-8 -mx-2">
                <Field label={t('partner_id')} value={data?.partner_id} />
                <Field label={t('unsubscribe')} value={data?.is_unsubscribe ? t('true') : t('false')} />
                <Field label={t('date_time')} value={data?.date_time ? new Date(data.date_time).toLocaleString() : '-'} />
                <Field label={t('subscription_url')} value={data?.subscription_url} />
                <Field label={t('callback_url')} value={data?.registry_callback_url} />
                <div className="pt-4">
                    <span className="text-secondary-third text-[16px] font-medium block mb-2">{t('description')}</span>
                    <div className="text-neutral-first text-[16px] font-bold bg-neutral-second p-4 rounded-lg border border-secondary-first">
                        {data?.description || '-'}
                    </div>
                </div>

                <div className="pt-6">
                    <span className="text-secondary-third text-[16px] font-medium block mb-2">{t('header')}</span>
                    {renderJSON(data?.header)}
                </div>

                <div className="pt-4">
                    <span className="text-secondary-third text-[16px] font-medium block mb-2">{t('payload')}</span>
                    {renderJSON(data?.payload)}
                </div>

                <div className="pt-4">
                    <span className="text-secondary-third text-[16px] font-medium block mb-2">{t('response')}</span>
                    {renderJSON(data?.response)}
                </div>
            </div>
        </BaseModal>
    );
}
