import { useFetch } from "@/shared/hooks/useFetch";

export const useIntakeFormTabs = (formId?: string) => {
    const { data, loading, error } = useFetch<any>({
        url: "/api/intake-form/get-all-intake-form-tabs",
        options: {
            method: "POST",
            body: JSON.stringify({
                form_id: formId
            }),
        },
        enabled: !!formId,
    });

    return {
        tabs: data?.intake_form_tabs || [],
        loading,
        error,
    };
};
