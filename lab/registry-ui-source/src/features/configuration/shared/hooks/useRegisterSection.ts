import { useFetch } from '@/shared/hooks';

export function useRegisterSection(register_id: string, section_id: string) {
    const { data, loading, error, execute } = useFetch<{
        section: any;
        pagination?: {
            number_of_items: number;
            number_of_pages: number;
        };
    }>({
        url: '/api/configuration/registers/section-metadata/get-section',
        options: {
            method: 'POST',
            body: JSON.stringify({
                register_id: register_id,
                section_id: section_id
            })
        },
        enabled: !!register_id && !!section_id
    });

    return {
        section: data?.section,
        pagination: data?.pagination,
        loading,
        error,
        refresh: execute,
    };
}
