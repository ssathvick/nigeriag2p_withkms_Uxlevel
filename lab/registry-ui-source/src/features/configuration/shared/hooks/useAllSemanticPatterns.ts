import { useFetch } from '@/shared/hooks';

export interface IncomingSemanticPattern {
    semantic_pattern_id: string;
    data_model_id: string;
    data_model_mnemonic?: string;
    register_id: string;
    register_mnemonic?: string;
    intake_form_id: string;
    intake_form_mnemonic?: string;
    pattern_for_register: string;
    pattern_for_intake_form: string;
    key_path_for_business_payload: string;
    raw_payload_enricher_class: string;
}

export function useAllSemanticPatterns(page?: number, pageSize?: number) {
    const { data, loading, error, execute } = useFetch<{
        semantic_patterns: IncomingSemanticPattern[];
        pagination?: {
            number_of_items: number;
            number_of_pages: number;
        };
    }>({
        url: '/api/configuration/ingest/get-all-semantic-patterns',
        options: {
            method: 'POST',
            body: JSON.stringify({
                pagination_request: {
                    current_page: page,
                    page_size: pageSize
                }
            })
        }
    });

    const semanticPatterns = data?.semantic_patterns || [];

    return {
        semanticPatterns,
        pagination: data?.pagination,
        loading,
        error,
        refresh: execute,
    };
}
