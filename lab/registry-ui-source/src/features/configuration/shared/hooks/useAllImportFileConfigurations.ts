import { useFetch } from '@/shared/hooks';

export interface ImportFileConfiguration {
    import_file_configuration_id: string;
    register_id: string;
    form_id: string;
    data_model_id: string;
    import_file_template_mnemonic: string;
    import_file_template_description: string;
}

export function useAllImportFileConfigurations(
    registerId: string,
    currentPage: number = 1,
    pageSize: number = 10,
) {
    const { data, loading, error, execute } = useFetch<{
        import_file_configurations: ImportFileConfiguration[];
        pagination?: {
            number_of_items: number;
            number_of_pages: number;
        };
    }>({
        url: '/api/input-mechanism/get-import-file-configuration',
        enabled: !!registerId,
        options: {
            method: 'POST',
            body: JSON.stringify({
                current_page: currentPage,
                page_size: pageSize,
                register_id: registerId,
            }),
        },
    });

    return {
        importFileConfigurations: data?.import_file_configurations || [],
        pagination: data?.pagination,
        loading,
        error,
        refresh: execute,
    };
}
