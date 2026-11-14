import { useFetch } from '@/shared/hooks';

export interface SubscriptionActivityLog {
    subscription_activity_log_id: string;
    is_unsubscribe: boolean;
    description: string;
    partner_id: string;
    subscription_url: string;
    registry_callback_url: string;
    header: any;
    payload: any;
    response: any;
    date_time: string;
}

export function useAllSubscriptionActivityLogs(page?: number, pageSize?: number) {
    const { data, loading, error, execute } = useFetch<{
        activity_logs: SubscriptionActivityLog[];
        pagination?: {
            number_of_items: number;
            number_of_pages: number;
        };
    }>({
        url: '/api/configuration/ingest/get-all-subscription-activity-logs',
        options: {
            method: 'POST',
            body: JSON.stringify({
                current_page: page,
                page_size: pageSize
            })
        }
    });

    const activityLogs = data?.activity_logs || [];

    return {
        activityLogs,
        pagination: data?.pagination,
        loading,
        error,
        refresh: execute,
    };
}
