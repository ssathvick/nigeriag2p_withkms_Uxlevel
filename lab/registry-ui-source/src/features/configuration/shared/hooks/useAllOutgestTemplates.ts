import { useFetch } from '@/shared/hooks';

export interface OutgestTemplate {
    template_id: string;
    register_id: string;
    register_mnemonic: string;
    data_model_id: string;
    data_model_mnemonic: string;
    template_file_id: string;
}

export function useAllOutgestTemplates(page?: number, pageSize?: number) {
    const { data, loading, error, execute } = useFetch<{
        templates: OutgestTemplate[];
        pagination?: {
            number_of_items: number;
            number_of_pages: number;
        };
    }>({
        url: '/api/configuration/outgest/all-templates',
        options: {
            method: 'POST',
            body: JSON.stringify({
                current_page: page,
                page_size: pageSize
            })
        }
    });

    return {
        templates: data?.templates || [],
        pagination: data?.pagination,
        loading,
        error,
        refresh: execute,
    };
}
