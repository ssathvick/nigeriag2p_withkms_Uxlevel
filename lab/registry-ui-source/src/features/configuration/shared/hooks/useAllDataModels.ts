import { useFetch } from '@/shared/hooks';

export interface DataModel {
    data_model_id: string;
    data_model_mnemonic: string;
    pattern_for_data_model: string;
    response_template_file_id: string;
    is_active: boolean;
}

export function useAllDataModels(page?: number, pageSize?: number) {
    const { data, loading, error, execute } = useFetch<{
        data_models: DataModel[];
        pagination?: {
            number_of_items: number;
            number_of_pages: number;
        };
    }>({
        url: '/api/configuration/data-models/all',
        options: {
            method: 'POST',
            body: JSON.stringify({
                current_page: page,
                page_size: pageSize
            })
        }
    });

    return {
        dataModels: data?.data_models || [],
        pagination: data?.pagination,
        loading,
        error,
        refresh: execute,
    };
}
