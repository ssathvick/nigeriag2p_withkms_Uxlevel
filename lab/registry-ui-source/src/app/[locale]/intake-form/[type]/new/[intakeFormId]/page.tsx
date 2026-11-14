'use client';

import { useParams, useRouter } from 'next/navigation';
import { TopBar } from '@/components/shared';
import MultiSectionAccordionForms from '@/features/intake-form/components/MultiSectionAccordionForms';
import { useRegister } from '@/context/RegisterContext';
import { useIntakeFormDetails } from '@/features/intake-form/hooks/useIntakeFormDetails';
import { useTranslations } from 'next-intl';
import { useIntakeFormSectionAction } from '@/features/intake-form/hooks/useIntakeFormSectionAction';

export default function NewIntakeFormSubmissionPage() {
    const t = useTranslations();
    const router = useRouter();
    const routeParams = useParams<{ type: string, intakeFormId: string }>();
    const intake_form_id = routeParams.intakeFormId;
    const registerType = routeParams.type;

    const { currentRegister } = useRegister();
    const registerId = currentRegister?.register_id;

    const { sections, form_name, form_description, loading } = useIntakeFormDetails(intake_form_id);

    const { handleAction, FormActionModals } = useIntakeFormSectionAction({
        registerId,
        formId: intake_form_id,
        registerType,
        submissionId: null
    });

    return (
        <div className="min-h-screen mx-auto bg-secondary-first">
            <TopBar
                breadcrumb={[
                    {
                        label: t("register_intake_form", { subject: currentRegister?.register_subject || t("register") }),
                        href: `/intake-form/${registerType}`
                    },
                    { label: form_name || "" }
                ]}

                showFilters={false}
                showPagination={false}
                showCapsule={false}
            />

            <div className="mx-7.5">
                {loading ? (
                    <div className="flex items-center justify-center py-20">
                        <span className="text-neutral-first/50">{t('loading')}</span>
                    </div>
                ) : (
                    <MultiSectionAccordionForms
                        formDetailsCard={true}
                        sections={sections || []}
                        form_name={form_name}
                        form_description={form_description}
                        onAction={handleAction}
                        onCancel={() => router.push(`/intake-form/${registerType}`)}
                        registerType={registerType}
                    />

                )}
            </div>

            <FormActionModals />
        </div>
    );
}
