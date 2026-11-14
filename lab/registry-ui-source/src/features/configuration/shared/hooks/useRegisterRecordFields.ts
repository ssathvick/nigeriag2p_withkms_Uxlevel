import { useFetch } from '@/shared/hooks';

export interface RegisterRecordField {
    field_name: string;
    data_type: string;
    required: boolean;
    nullable: boolean;
}

export function useRegisterRecordFields(registerId: string) {
    const { data, loading, error, execute } = useFetch<{
        register_id: string;
        register_mnemonic: string;
        fields: RegisterRecordField[];
        pagination?: {
            number_of_items: number;
            number_of_pages: number;
        };
    }>({
        url: '/api/configuration/data-policy/get-register-record-fields',
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
        fields: data?.fields || [],
        registerMnemonic: data?.register_mnemonic,
        loading,
        error,
        refresh: execute,
    };
}
