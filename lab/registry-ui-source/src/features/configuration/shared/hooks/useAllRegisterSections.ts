import { useFetch } from '@/shared/hooks';

export function useAllRegisterSections(register_id?: string, page?: number, pageSize?: number) {
    const { data, loading, error, execute } = useFetch<{
        sections: any[];
        pagination?: {
            number_of_items: number;
            number_of_pages: number;
        };
    }>({
        url: '/api/configuration/registers/section-metadata/get-all-sections',
        options: {
            method: 'POST',
            body: JSON.stringify({
                register_id: register_id,
                current_page: page,
                page_size: pageSize
            })
        },
        enabled: !!register_id
    });

    return {
        sections: data?.sections,
        pagination: data?.pagination,
        loading,
        error,
        refresh: execute,
    };
}
