import { useFetch } from "@/shared/hooks/useFetch";

export function useIntakeDeduplication(submissionId: string, type: "intake-form" | "register") {
    const { data, loading } = useFetch({
        enabled: !!submissionId,
        url: type === 'intake-form'
            ? '/api/intake-form/get-deduplication-intake-form-intake-form-results'
            : '/api/intake-form/get-deduplication-intake-form-register-results',
        options: {
            method: 'POST',
            body: JSON.stringify({
                submission_id: submissionId,
                current_page: 1,
                page_size: 20,
            }),
        }
    });

    return {
        results: data || [],
        loading
    };
}
