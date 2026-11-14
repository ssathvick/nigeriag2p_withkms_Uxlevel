import { useState } from 'react';
import { useFetch } from '@/shared/hooks';
import { SubscriptionActivityLog } from './useAllSubscriptionActivityLogs';
import { useTranslations } from 'next-intl';
import { toast } from 'react-toastify';

export function useSubscriptionActivityLog() {
    const t = useTranslations();
    const [selectedActivityLog, setSelectedActivityLog] = useState<SubscriptionActivityLog | undefined>(undefined);
    const { execute, loading, error } = useFetch<SubscriptionActivityLog>();

    const fetchActivityLog = async (id: string) => {
        try {
            const result = await execute('/api/configuration/ingest/get-subscription-activity-log-for-partner', {
                method: 'POST',
                body: JSON.stringify({ subscription_activity_log_id: id })
            });
            if (result) {
                setSelectedActivityLog(result);
            }
            return result;
        } catch (error) {
            toast.error(t('toast_operation_failed'));
            return null;
        }
    };

    return {
        selectedActivityLog,
        setSelectedActivityLog,
        fetchActivityLog,
        loading,
        error
    };
}
