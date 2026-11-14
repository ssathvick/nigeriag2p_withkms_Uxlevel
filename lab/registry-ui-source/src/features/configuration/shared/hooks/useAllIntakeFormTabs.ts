import { useFetch } from '@/shared/hooks';

export function useAllIntakeFormTabs(page?: number, pageSize?: number, intakeFormId?: string) {
    const { data, loading, error, execute } = useFetch<{
        intake_form_tabs: any[];
        pagination?: {
            number_of_items: number;
            number_of_pages: number;
        };
    }>({
        url: '/api/configuration/intake-forms/get-all-intake-form-tabs',
        options: {
            method: 'POST',
            body: JSON.stringify({
                current_page: page,
                page_size: pageSize,
                form_id: intakeFormId
            })
        }
    });

    return {
        intake_form_tabs: data?.intake_form_tabs,
        pagination: data?.pagination,
        loading,
        error,
        refresh: execute,
    };
}
