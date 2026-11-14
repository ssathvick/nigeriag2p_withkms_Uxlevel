import { useFetch } from '@/shared/hooks/useFetch';
import { useRegister } from '@/context/RegisterContext';

export interface VCConfig {
    vc_config_id: string;
    register_id: string;
    intake_form_id: string;
    data_model_id: string;
    vc_mnemonic: string;
    descriptor_schema: Record<string, unknown>;
}

export const useVCConfigs = () => {
    const { currentRegister } = useRegister();
    const registerId = currentRegister?.register_id;

    const { data, loading } = useFetch<VCConfig[]>({
        url: '/api/input-mechanism/get-vc-configuration',
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
        vcOptions: data ?? [],
        isLoadingVCs: loading,
    };
};
