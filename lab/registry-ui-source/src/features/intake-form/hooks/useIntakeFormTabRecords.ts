import { useFetch } from "@/shared/hooks/useFetch";

export const useIntakeFormTabRecords = (submissionId?: string, tabId?: string) => {
    const { data, loading, error } = useFetch<any>({
        url: "/api/intake-form/get-intake-form-tab-records",
        options: {
            method: "POST",
            body: JSON.stringify({
                submission_id: submissionId,
                tab_id: tabId
            }),
        },
        enabled: !!(submissionId && tabId),
    });


    return {
        section_payloads: data?.section_payloads,
        loading,
        error
    };
};
