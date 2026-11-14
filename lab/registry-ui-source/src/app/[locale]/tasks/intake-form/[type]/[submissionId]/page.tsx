'use client';

import { useMemo } from 'react';
import { useParams } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { useRegister } from '@/context/RegisterContext';
import IntakeFormSubmissionView from '@/features/intake-form/components/IntakeFormSubmissionView';

export default function TaskIntakeFormDetailPage() {
    const t = useTranslations();
    const { type, submissionId } = useParams<{ type: string; submissionId: string }>();
    const { currentRegister } = useRegister();

    const breadcrumb = useMemo(
        () => [
            { label: t('tasks'), href: '/tasks/intake-form' },
            { label: t('tasks_intake') },
            {
                label: t('register_intake_form', {
                    subject: currentRegister?.register_subject || t('register'),
                }),
            },
            {
                label: submissionId ? `${t('id')}-•••${submissionId.slice(-3)}` : '',
            },
        ],
        [currentRegister?.register_subject, submissionId, t],
    );

    return (
        <IntakeFormSubmissionView
            registerType={type}
            submissionId={submissionId}
            breadcrumb={breadcrumb}
        />
    );
}
