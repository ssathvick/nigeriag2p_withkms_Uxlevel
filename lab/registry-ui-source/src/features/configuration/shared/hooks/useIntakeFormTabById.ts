import { useFetch } from '@/shared/hooks';

export function useIntakeFormTabById(tabId: string) {
    const { data, loading, error, execute } = useFetch<{
        tab: any;
    }>({
        url: '/api/configuration/intake-forms/get-tab-by-id',
        options: {
            method: 'POST',
            body: JSON.stringify({
                tab_id: tabId
            })
        },
    });

    return {
        tab: data?.tab,
        loading,
        error,
        refresh: execute,
    };
}
