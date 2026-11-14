import { useFetch } from "@/shared/hooks/useFetch";
import { IntakeForm } from "../types/intake-form";

export const useIntakeForms = (registerId?: string) => {
    const { data, loading, error } = useFetch<any>({
        url: "/api/intake-form/get-all-intake-forms",
        options: {
            method: "POST",
            body: JSON.stringify({ register_id: registerId }),
        },
        enabled: !!registerId,
    });

    return {
        forms: (data?.intake_forms ?? []) as IntakeForm[],
        loading,
        error,
    };
};
