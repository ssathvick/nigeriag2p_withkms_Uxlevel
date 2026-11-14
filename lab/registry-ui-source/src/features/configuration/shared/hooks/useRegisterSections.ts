import { useFetch } from '@/shared/hooks';

interface Section {
    section_id: string;
    section_mnemonic: string;
}

export function useRegisterSections(registerId: string) {
    const { data, loading, error, execute } = useFetch<Section[]>({
        url: '/api/register/get-register-sections',
        enabled: !!registerId,
        options: {
            method: 'POST',
            body: JSON.stringify({ register_id: registerId })
        }
    });

    return {
        sections: data || [],
        loading,
        error,
        refresh: execute
    };
}
