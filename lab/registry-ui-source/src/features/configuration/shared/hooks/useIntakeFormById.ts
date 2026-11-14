import { useFetch } from '@/shared/hooks';

export function useIntakeFormById(intakeFormId: string) {
    const { data, loading, error, execute } = useFetch<{
        intake_form: any;
    }>({
        url: '/api/configuration/intake-forms/get-intake-form-by-id',
        options: {
            method: 'POST',
            body: JSON.stringify({
                form_id: intakeFormId
            })
        },
    });

    return {
        intake_form: data?.intake_form,
        loading,
        error,
        refresh: execute,
    };
}
