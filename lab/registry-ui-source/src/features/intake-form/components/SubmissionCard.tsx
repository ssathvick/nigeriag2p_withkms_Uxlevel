'use client';

import { WorkflowStatus } from '@/components/shared/Workflow';
import { Link } from '@/i18n/navigation';
import { KeyValue } from '@/components/ui/KeyValue';
import { IntakeFormSubmission } from '../types/intake-form';
import { useTranslations } from 'next-intl';

interface IntakeFormSubmissionCardProps {
    submission: IntakeFormSubmission;
    registerType: string;
}

export function IntakeFormSubmissionCard({ submission, registerType }: IntakeFormSubmissionCardProps) {
    const t = useTranslations();

    const formatLabel = (label: string) => {
        return label
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    };

    return (
        <Link
            href={`/intake-form/${registerType}/submission/${submission.submission_id}`}
            className="group block w-full"
        >
            <div className="rounded-[10px] bg-neutral-second px-10 py-8 shadow-sm transition-shadow duration-200 group-hover:shadow-md">
                <div className="flex justify-between items-start gap-4"><h3
                    className="text-[20px] font-semibold leading-snug tracking-tight text-primary-second line-clamp-2 md:text-[22px] mb-4"
                    title={submission.record_name ?? undefined}
                >
                    {submission.record_name ?? '—'}
                </h3><WorkflowStatus approval={submission.approval_status} draft={submission.draft_status} summary={submission.awe_request_status_summary}/></div>
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 items-stretch gap-6 text-[14px] text-neutral-first/50">
                    <div className="flex h-full min-h-0 flex-col">
                        <div className="flex flex-1 flex-col space-y-1">
                            <KeyValue label="Reference" value={submission.application_reference || 'Not recorded'} />

                            <KeyValue label={t('draft_status')} value={submission.draft_status} />
                            <KeyValue label={t('approval_status')} value={submission.approval_status} />
                        </div>
                    </div>


                    <div className="space-y-4">
                        <div className="space-y-1 border-l-2 border-secondary-second pl-6">
                            {/* <KeyValue
                                label={t('no_of_verifications_required') || "No of Verifications Required"}
                                value={String(submission.number_of_verifications_required)}
                            />
                            <KeyValue
                                label={t('no_of_verifications_done') || "No of Verifications Done"}
                                value={String(submission.number_of_verifications_done)}
                            /> */}
                            <KeyValue
                                label={t('created_by') || "Created By"}
                                value={submission.created_by}
                            />
                            <KeyValue
                                label={t('register_ingest_process_status')}
                                value={submission.register_ingest_process_status || '--'}
                            />
                        </div>
                    </div>

                    <div className="flex h-full min-h-0 flex-col">
                        <div className="flex flex-1 flex-col space-y-1 border-l-2 border-secondary-second pl-6">
                            {submission.display_fields?.slice(0, Math.ceil((submission.display_fields?.length || 0) / 2)).map((field) => (
                                <KeyValue
                                    key={field.field_name}
                                    label={formatLabel(field.field_name)}
                                    value={String(field.value ?? '--')}
                                />
                            ))}
                        </div>
                    </div>

                    <div className="flex h-full min-h-0 flex-col">
                        <div className="flex flex-1 flex-col space-y-1 border-l-2 border-secondary-second pl-6">
                            {submission.display_fields?.slice(Math.ceil((submission.display_fields?.length || 0) / 2)).map((field) => (
                                <KeyValue
                                    key={field.field_name}
                                    label={formatLabel(field.field_name)}
                                    value={String(field.value ?? '--')}
                                />
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </Link>
    );
}
