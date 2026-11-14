import { useFetch } from '@/shared/hooks';

export interface IncomingKeyPath {
    key_path_id: string;
    data_model_id: string;
    data_model_mnemonic?: string;
    key_path_for_message_id?: string;
    key_path_for_sender?: string;
    key_path_for_signature?: string;
    key_path_for_signature_payload?: string;
    is_list: boolean;
    key_path_for_list_elements?: string;
}

export function useAllIncomingKeyPaths(page?: number, pageSize?: number) {
    const { data, loading, error, execute } = useFetch<{
        key_paths: IncomingKeyPath[];
        pagination?: {
            number_of_items: number;
            number_of_pages: number;
        };
    }>({
        url: '/api/configuration/ingest/all-key-paths',
        options: {
            method: 'POST',
            body: JSON.stringify({
                current_page: page,
                page_size: pageSize
            })
        }
    });

    const keyPaths = data?.key_paths || [];

    return {
        keyPaths,
        pagination: data?.pagination,
        loading,
        error,
        refresh: execute,
    };
}
