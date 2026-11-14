import { useFetch } from '@/shared/hooks';

export function useAllIntakeForms(page?: number, pageSize?: number, registerId?: string) {
    const { data, loading, error, execute } = useFetch<{
        intake_forms: any[];
        pagination?: {
            number_of_items: number;
            number_of_pages: number;
        };
    }>({
        url: '/api/configuration/intake-forms/get-all-intake-forms',
        options: {
            method: 'POST',
            body: JSON.stringify({
                current_page: page,
                page_size: pageSize,
                ...(registerId ? { register_id: registerId } : {}),
            }),
        },
    });

    return {
        intake_forms: data?.intake_forms,
        pagination: data?.pagination,
        loading,
        error,
        refresh: execute,
    };
}
