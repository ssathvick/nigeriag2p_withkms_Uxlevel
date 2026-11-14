'use client';

import { useParams } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { useRegister } from '@/context/RegisterContext';
import IntakeFormSubmissionView from '@/features/intake-form/components/IntakeFormSubmissionView';

export default function IntakeFormSubmissionPage() {
    const t = useTranslations();
    const routeParams = useParams<{ type: string; submissionId: string }>();
    const submissionId = routeParams.submissionId;
    const registerType = routeParams.type;
    const { currentRegister } = useRegister();

    return (
        <IntakeFormSubmissionView
            registerType={registerType}
            submissionId={submissionId}
            breadcrumb={[
                {
                    label: t('register_intake_form', {
                        subject: currentRegister?.register_subject || t('register'),
                    }),
                    href: `/intake-form/${registerType}`,
                },
                {
                    label: submissionId ? `${t('id')}-•••${submissionId.slice(-3)}` : '',
                },
            ]}
        />
    );
}
