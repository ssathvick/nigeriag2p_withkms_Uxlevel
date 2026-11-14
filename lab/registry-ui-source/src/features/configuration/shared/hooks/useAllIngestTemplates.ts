import { useFetch } from '@/shared/hooks';

export interface IngestTemplate {
    template_id: string;
    register_id: string;
    register_mnemonic: string;
    data_model_id: string;
    data_model_mnemonic: string;
    template_file_id: string;
    jsonld_expansion_required: boolean;
}

export function useAllIngestTemplates(page?: number, pageSize?: number) {
    const { data, loading, error, execute } = useFetch<{
        templates: IngestTemplate[];
        pagination?: {
            number_of_items: number;
            number_of_pages: number;
        };
    }>({
        url: '/api/configuration/ingest/all-templates',
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
