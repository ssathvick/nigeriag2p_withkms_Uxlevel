import { useFetch } from "@/shared/hooks/useFetch";
import { RenderedIntakeForm } from "../types/intake-form";

export const useIntakeFormDetails = (intakeFormId?: string) => {
    const { data, loading, error } = useFetch<RenderedIntakeForm>({
        url: "/api/intake-form/render-intake-form",
        options: {
            method: "POST",
            body: JSON.stringify({
                form_id: intakeFormId
            }),
        },
        enabled: !!(intakeFormId),
    });


    return {
        sections: data?.tabs[0].sections?.slice().sort((a, b) => a.section_order - b.section_order),
        // TODO: Assuming only one tab for now, may need to be updated later
        form_name: data?.form_mnemonic,
        form_description: data?.form_description,
        loading,
        error,
    };
};
