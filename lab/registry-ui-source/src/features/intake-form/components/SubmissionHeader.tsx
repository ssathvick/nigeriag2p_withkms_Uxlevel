'use client';

import { PrivateIdentifier,WorkflowStatus } from '@/components/shared/Workflow';
import Image from "next/image";
import { useTranslations } from "next-intl";
import { IntakeFormSubmission } from "../types/intake-form";
import { toast } from "react-toastify";
import { useFetch } from "@/shared/hooks/useFetch";
import { useMemo } from "react";
import { useIntakeFormDocuments } from "../hooks/useIntakeFormDocuments";
import { UploadedDocument } from "@/shared/types";
import { formatDate } from "@/shared/utils/dateUtils";
import Can from "@/components/shared/Can";
import { INTAKE_FORM_ACTIONS } from "../utils/intakeForm.actions";

const statusClassMap: Record<string, string> = {
    REJECTED: "text-toast-failed",
    PENDING: "text-amber-500",
    APPROVED: "text-toast-success",
    DRAFT: "text-toast-info",
    SUBMITTED: "text-indigo-500",
    FINALIZED: "text-toast-success",
};

interface Props {
    submission?: IntakeFormSubmission | null;
    section_payloads?: any[] | null;
    onActionComplete?: () => void;
}

export default function SubmissionHeader({ submission, section_payloads, onActionComplete }: Props) {
    const t = useTranslations();
    const { execute, loading: loadingAction } = useFetch({ enabled: false });

    const documents = useMemo(() => {
        const allDocs: UploadedDocument[] = [];
        section_payloads?.forEach(section => {
            if (section.documents) {
                allDocs.push(...section.documents);
            }
        });
        return allDocs;
    }, [submission, section_payloads]);

    const { documents: docsWithUrls } = useIntakeFormDocuments(documents);

    const handleAction = async (type: 'approve' | 'reject') => {
        if (!submission?.submission_id) return;

        try {
            const url = type === 'approve'
                ? '/api/intake-form/approve-intake-form-submission'
                : '/api/intake-form/reject-intake-form-submission';

            const result = await execute(url, {
                method: 'POST',
                body: JSON.stringify({ submission_id: submission.submission_id }),
            });

            if (result?.approval_status == "APPROVED" || result?.approval_status == "REJECTED") {
                toast.success(t('toast_submission_success', { type }));
                onActionComplete?.();
            } else {
                toast.error(t('toast_submission_fail', { type }));
            }
        } catch (error) {
            toast.error(t('toast_submission_error', { type }));
        }
    };

    return (
        <div className="rounded-[10px] bg-primary-first/20 px-10 py-5 flex flex-col border border-dashed border-primary-second">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <InfoSection submission={submission} />
                <VerificationStats submission={submission} documentsCount={documents.length} />
                <AttachedDocuments documents={docsWithUrls} />
            </div>

            {/* Approve / reject hidden from view
            {submission?.approval_status === "PENDING" && (
                <Can action={INTAKE_FORM_ACTIONS.approve}>
                    <div className="my-4 border-t-2 border-primary-first" />
                    <div className="flex items-center gap-4">
                        <button
                            type="button"
                            onClick={() => handleAction('reject')}
                            className="px-4 py-2 text-[14px] font-medium rounded-[10px] bg-neutral-second text-neutral-first/50"
                        >
                            {t('reject_submission')}
                        </button>

                        <button
                            type="button"
                            onClick={() => handleAction('approve')}
                            className="px-4 py-2 text-[14px] font-medium rounded-[10px] bg-neutral-first text-neutral-second"
                        >
                            {t('approve_submission')}
                        </button>
                    </div>
                </Can>
            )}
            */}
        </div>
    );
}

const InfoSection = ({ submission }: { submission?: IntakeFormSubmission | null }) => {
    const t = useTranslations();
    return (
        <div className="space-y-2 text-[16px] text-neutral-first/50">
            <h3 className="text-[24px] font-medium text-neutral-first truncate" title={t('intake_submission') || 'Intake Submission'}>
                {submission?.record_name || t('intake_submission')}
            </h3>
            <WorkflowStatus approval={submission?.approval_status} draft={submission?.draft_status} summary={submission?.awe_request_status_summary}/>
            <div className="flex gap-4"><span className="w-1/2">Source:</span><strong>{submission?.submission_source==='ODK_COLLECT' || submission?.created_by?.includes('ODK')?'Offline data collection · ODK Collect':'Online staff intake'}</strong></div>
            <div className="flex gap-4"><span className="w-1/2">Reference:</span><strong>{submission?.application_reference || "Not recorded"}</strong></div>
            <div className="flex w-full overflow-hidden">
                <span className="w-1/2 truncate" title={t('submission_id')}>{t('submission')}:</span>
                <span className="w-1/2 pl-4 text-neutral-first font-medium truncate" title={submission?.submission_id ? String(submission.submission_id) : ''}>
                    <PrivateIdentifier value={submission?.submission_id}/>
                </span>
            </div>
            <div className="flex w-full overflow-hidden">
                <span className="w-1/2 truncate" title={t('draft_status')}>{t('draft_status')}:</span>
                <span className={`w-1/2 pl-4 font-medium truncate ${statusClassMap[submission?.draft_status || ''] ?? "text-neutral-first/50"}`} title={submission?.draft_status}>
                    {submission?.draft_status}
                </span>
            </div>
            <div className="flex w-full overflow-hidden">
                <span className="w-1/2 truncate" title={t('approval_status')}>{t('approval_status')}:</span>
                <span className={`w-1/2 pl-4 font-medium truncate ${statusClassMap[submission?.approval_status || ''] ?? "text-neutral-first/50"}`} title={submission?.approval_status}>
                    {submission?.approval_status}
                </span>
            </div>
            <div className="flex w-full overflow-hidden">
                <span className="w-1/2 truncate" title={t('created_by')}>{t('created_by')}:</span>
                <span className="w-1/2 pl-4 text-neutral-first font-medium truncate" title={submission?.created_by || '--'}>
                    {submission?.created_by || '--'}
                </span>
            </div>
            <div className="flex w-full overflow-hidden">
                <span className="w-1/2 truncate" title={t('register_ingest_process_status')}>{t('register_ingest_process_status')}:</span>
                <span className={`w-1/2 pl-4 font-medium truncate ${statusClassMap[submission?.register_ingest_process_status || ''] ?? "text-neutral-first/50"}`} title={submission?.register_ingest_process_status || '--'}>
                    {submission?.register_ingest_process_status || '--'}
                </span>
            </div>
        </div>
    );
};

const VerificationStats = ({
    submission,
    documentsCount
}: {
    submission?: IntakeFormSubmission | null;
    documentsCount: number;
}) => {
    const t = useTranslations();
    return (
        <div className="space-y-2 text-[16px] text-neutral-first/50">
            <h3 className="text-lg font-semibold text-neutral-first invisible">
                Verification
            </h3>

            <div className="border-l border-primary-first pl-6 space-y-2">
                {/* Verifications required / done hidden from view
                <div className="flex w-full overflow-hidden">
                    <span className="w-1/2 truncate" title={t('verifications_required')}>{t('verifications_required')}:</span>
                    <span className="w-1/2 pl-4 text-neutral-first font-medium truncate" title={submission?.number_of_verifications_required !== undefined ? String(submission.number_of_verifications_required) : ''}>
                        {submission?.number_of_verifications_required}
                    </span>
                </div>

                <div className="flex w-full overflow-hidden">
                    <span className="w-1/2 truncate" title={t('verifications_done')}>{t('verifications_done')}:</span>
                    <span className="w-1/2 pl-4 text-neutral-first font-medium truncate" title={submission?.number_of_verifications_done !== undefined ? String(submission.number_of_verifications_done) : ''}>
                        {submission?.number_of_verifications_done}
                    </span>
                </div>
                */}

                <div className="flex w-full overflow-hidden">
                    <span className="w-1/2 truncate" title={t('documents_attached')}>{t('documents_attached')}:</span>
                    <span className="w-1/2 pl-4 text-neutral-first font-medium truncate" title={documentsCount.toString()}>
                        {documentsCount}
                    </span>
                </div>
            </div>
        </div>
    );
};

const AttachedDocuments = ({ documents = [] }: { documents?: any[] }) => {
    const t = useTranslations();

    const visibleDocs = documents.slice(0, 3);
    const placeholdersCount = Math.max(0, 3 - visibleDocs.length);

    return (
        <div className="space-y-2 text-[16px] text-neutral-first/50">
            <div className="pl-6 flex items-center leading-none mt-2">
                <span className="text-[16px] font-medium text-neutral-first">
                    {t('attached_documents')}
                </span>
                <Image
                    src="/images/changerequest/attached_doc_icon.png"
                    alt={t('document_icon_alt')}
                    width={14}
                    height={14}
                    className="ml-1 mb-1"
                />
            </div>

            <div className="border-l border-primary-first pl-6 flex flex-col gap-2 font-semibold min-h-15">


                {visibleDocs.map((doc, index) => (

                    <a
                        key={index}
                        href={doc.document_url ? doc.document_url : "#"}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={`flex items-center gap-2 ${doc.document_url
                            ? 'cursor-pointer hover:underline text-neutral-first'
                            : 'opacity-50 pointer-events-none'
                            }`}
                    >
                        {doc.document_label}
                        <Image src="/images/common/arrow_next_01.png" alt={t('arrow')} width={14} height={14} />
                    </a>
                ))}

                {Array.from({ length: placeholdersCount }).map((_, i) => (
                    <span key={i} className="invisible">placeholder</span>
                ))}

            </div>
        </div>
    );
};
