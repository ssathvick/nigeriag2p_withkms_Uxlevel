import { useFetch } from '@/shared/hooks';

export function useConfigTabs(registerId: string, page: number = 1, pageSize: number = 10) {
    const { data, loading, error, execute } = useFetch<{
        tabs: any[];
        pagination?: {
            number_of_items: number;
            number_of_pages: number;
        };
    }>({
        url: '/api/configuration/registers/tab-metadata/get-all-tabs',
        options: {
            method: 'POST',
            body: JSON.stringify({
                register_id: registerId,
                page,
                pageSize
            })
        }
    });

    // Ascending order
    const tabs = [...(data?.tabs || [])]
        .sort((a, b) => (a.tab_order ?? 0) - (b.tab_order ?? 0));

    return {
        tabs,
        pagination: data?.pagination,
        loading,
        error,
        refresh: execute
    };
}
