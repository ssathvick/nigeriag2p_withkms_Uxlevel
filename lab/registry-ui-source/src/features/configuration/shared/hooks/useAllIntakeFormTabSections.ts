import { useFetch } from '@/shared/hooks';

export function useAllIntakeFormTabSections(page?: number, pageSize?: number, tabId?: string) {
    const { data, loading, error, execute } = useFetch<{
        sections: any[];
        pagination?: {
            number_of_items: number;
            number_of_pages: number;
        };
    }>({
        url: '/api/configuration/intake-forms/get-all-tab-sections',
        options: {
            method: 'POST',
            body: JSON.stringify({
                current_page: page,
                page_size: pageSize,
                tab_id: tabId
            })
        }
    });

    return {
        sections: data?.sections,
        pagination: data?.pagination,
        loading,
        error,
        refresh: execute,
    };
}
