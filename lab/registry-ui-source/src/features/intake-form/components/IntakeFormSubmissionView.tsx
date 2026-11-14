'use client';

import { TopBar } from '@/components/shared';
import { useFetch } from '@/shared/hooks/useFetch';
import { ReviewHistory } from '@/components/shared/ReviewHistory';
import type {IntakeFormSubmission} from '../types/intake-form';
import { useIntakeFormDetails } from '@/features/intake-form/hooks/useIntakeFormDetails';
import { useIntakeFormTabs } from '@/features/intake-form/hooks/useIntakeFormTabs';
import { useIntakeFormTabRecords } from '@/features/intake-form/hooks/useIntakeFormTabRecords';
import MultiSectionAccordionForms from '@/features/intake-form/components/MultiSectionAccordionForms';
import SubmissionHeader from '@/features/intake-form/components/SubmissionHeader';
import { IntakeApprovalCard } from '@/features/approval/components';
import { parseAweCurrentStage } from '@/features/approval/utils/aweStatusSummary';
import { REGISTRY_INTAKE_FORM_ARTIFACT } from '@/features/approval/constants';
import { useTranslations } from 'next-intl';
import { useCallback, useMemo } from 'react';
import { useIntakeFormSectionAction } from '@/features/intake-form/hooks/useIntakeFormSectionAction';
import { RegisterFlattenedRecord } from '@/features/register/types';
import { useRegister } from '@/context/RegisterContext';
import { useRbac } from '@/context/RbacContext';
import { INTAKE_FORM_ACTIONS } from '@/features/intake-form/utils/intakeForm.actions';

interface BreadcrumbItem {
    label: string;
    href?: string;
}

interface IntakeFormSubmissionViewProps {
    registerType: string;
    submissionId: string;
    breadcrumb: BreadcrumbItem[];
}

export default function IntakeFormSubmissionView({
    registerType,
    submissionId,
    breadcrumb,
}: IntakeFormSubmissionViewProps) {
    const t = useTranslations();
    const { currentRegister } = useRegister();
    const { can } = useRbac();
    const canCreate = can(INTAKE_FORM_ACTIONS.edit);

    const registerId = currentRegister?.register_id;
    const detailOptions=useMemo(()=>({method:'POST' as const,body:JSON.stringify({submission_id:submissionId,register_id:registerId})}),[submissionId,registerId]);
    const {data:submission,loading:loadingSubmissions,execute:refetchSubmissions}=useFetch<IntakeFormSubmission>({url:'/api/intake-form/get-intake-form-submission',options:detailOptions,enabled:!!registerId});

    const refreshSubmissionView = useCallback(async () => {
        await refetchSubmissions('/api/intake-form/get-intake-form-submission',detailOptions);
    }, [refetchSubmissions,detailOptions]);

    const intakeApprovalArtifactContext = useMemo(() => {
        if (!submission?.submission_id) return null;
        const currentStage =
            parseAweCurrentStage(submission.awe_request_status_summary) ?? 1;
        return {
            artifactId: submission.submission_id,
            artifactType: REGISTRY_INTAKE_FORM_ARTIFACT,
            currentStage,
        };
    }, [submission?.submission_id, submission?.awe_request_status_summary]);

    const intakeFormId = submission?.form_id;
    const { sections, form_name, form_description, loading: loadingSections } =
        useIntakeFormDetails(intakeFormId);

    const { tabs, loading: loadingTabs } = useIntakeFormTabs(intakeFormId);
    const tabId = tabs[0]?.tab_id;

    const { section_payloads, loading: loadingRecords } = useIntakeFormTabRecords(
        submissionId,
        tabId,
    );

    const loading = loadingSubmissions || loadingSections || loadingTabs || loadingRecords;
    const isDraft = submission?.draft_status === 'DRAFT';

    const { handleAction, FormActionModals } = useIntakeFormSectionAction({
        registerId: submission?.register_id || '',
        formId: intakeFormId || '',
        registerType,
        submissionId,
        onSuccess: () => {},
    });

    const sectionDataMap = useMemo(() => {
        if (!section_payloads) return {};

        const map: Record<
            string,
            RegisterFlattenedRecord | { records: RegisterFlattenedRecord[] }
        > = {};

        for (const section of section_payloads) {
            if (!section.records?.length) continue;

            const existing = map[section.section_register_id];

            if (section.is_list === true) {
                if (existing && 'records' in existing) {
                    const existingList = existing as { records: RegisterFlattenedRecord[] };
                    existingList.records = [...existingList.records, ...section.records];
                } else {
                    map[section.section_register_id] = { records: [...section.records] };
                }
            } else {
                if (existing && !('records' in existing)) {
                    map[section.section_register_id] = { ...existing, ...section.records[0] };
                } else if (!existing) {
                    map[section.section_register_id] = { ...section.records[0] };
                }
            }
        }

        return map;
    }, [section_payloads]);

    return (
        <div className="min-h-screen mx-auto bg-secondary-first">
            <TopBar
                breadcrumb={breadcrumb}
                showFilters={false}
                showPagination={false}
                showCapsule={false}
            />

            <div className={`mx-7.5 ${isDraft ? '' : 'py-6 space-y-6'}`}>
                {loading ? (
                    <div className="flex items-center justify-center py-20">
                        <span className="text-neutral-first/50">{t('loading')}</span>
                    </div>
                ) : (
                    <div className="flex flex-col lg:flex-row gap-6">
                        <div className={`w-full ${isDraft ? '' : 'lg:w-[75%]'} space-y-6`}>
                            {!isDraft && (
                                <SubmissionHeader
                                    submission={submission}
                                    section_payloads={section_payloads}
                                    onActionComplete={() => window.location.reload()}
                                />
                            )}

                            {submission?.remarks && <section className="rounded-lg border border-amber-200 bg-amber-50 p-4"><h2 className="font-semibold">Review feedback</h2><p className="whitespace-pre-wrap">{submission.remarks}</p></section>}
                            <ReviewHistory events={submission?.review_history}/>
                            <MultiSectionAccordionForms
                                form_name={form_name}
                                form_description={form_description}
                                sections={sections || []}
                                schemaData={sectionDataMap}
                                showActions={isDraft && canCreate}
                                onAction={handleAction}
                                submissionId={submissionId}
                                registerType={registerType}
                            />
                        </div>

                        {!isDraft && (
                            <div className="w-full lg:w-[25%] space-y-6">
                                <IntakeApprovalCard
                                    awe_request_id={submission?.awe_request_id}
                                    artifactContext={intakeApprovalArtifactContext}
                                    isPending={
                                        !isDraft && submission?.approval_status === 'PENDING'
                                    }
                                    onRefresh={refreshSubmissionView}
                                />
                            </div>
                        )}
                    </div>
                )}
            </div>

            <FormActionModals />
        </div>
    );
}
