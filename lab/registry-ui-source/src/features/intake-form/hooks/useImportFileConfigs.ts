import { useFetch } from '@/shared/hooks/useFetch';
import { useRegister } from '@/context/RegisterContext';

export interface ImportFileConfig {
    import_file_configuration_id: string;
    register_id: string;
    form_id: string;
    data_model_id: string;
    import_file_template_mnemonic: string;
    import_file_template_description: string;
}

export const useImportFileConfigs = () => {
    const { currentRegister } = useRegister();
    const registerId = currentRegister?.register_id;

    const { data, loading } = useFetch<{
        import_file_configurations: ImportFileConfig[];
    }>({
        url: '/api/input-mechanism/get-import-file-configuration',
        enabled: !!registerId,
        options: {
            method: 'POST',
            body: JSON.stringify({
                register_id: registerId,
                current_page: 1,
                page_size: 100,
            }),
        },
    });

    return {
        importFileOptions: data?.import_file_configurations ?? [],
        isLoadingImportFiles: loading,
    };
};
