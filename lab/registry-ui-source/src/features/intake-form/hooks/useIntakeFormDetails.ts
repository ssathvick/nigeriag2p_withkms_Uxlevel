import { useFetch } from "@/shared/hooks/useFetch";
import {useTranslations} from 'next-intl';
import { RenderedIntakeForm } from "../types/intake-form";

export const useIntakeFormDetails = (intakeFormId?: string) => {
    const t=useTranslations();
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
        form_name: intakeFormId==='c1000000-0000-4000-8000-000000000002'?'Register your household':data?.form_mnemonic?t(data.form_mnemonic):undefined,
        form_description: data?.form_description,
        loading,
        error,
    };
};
