import Image from "next/image";
import {PrivateIdentifier,WorkflowStatus} from '@/components/shared/Workflow';
import { ChangeRequest } from "../types/change-request";
import { useTranslations } from "next-intl";
import { CHANGE_REQUEST_ACTIONS } from "../utils/changeRequest.actions";
import Can from "@/components/shared/Can";

export interface ChangeRequestDocument {
    document_label: string;
    document_store_id: string;
    document_url: string;
}

interface Props {
    details: ChangeRequest;
    verificationCount: number;
    documents?: ChangeRequestDocument[];
    onApprove: () => void;
    onReject: () => void;
    loadingAction: boolean;
}

const statusClassMap: Record<string, string> = {
    REJECTED: "text-toast-failed",
    PENDING: "text-amber-500",
    APPROVED: "text-toast-success",
};

export default function ChangeRequestHeader({
    details,
    verificationCount,
    documents = [],
    onApprove,
    onReject,
    loadingAction,
}: Props) {
    const t = useTranslations();
    const rawTitle = details?.record_name?.trim() || details?.section_mnemonic?.trim();

    const title = rawTitle
        ? t(rawTitle, { default: rawTitle })
        : t('change_request');
    return (
        <div className="registry-change-header rounded-[10px] bg-primary-first/20 px-10 pt-5 pb-4 flex flex-col border border-dashed border-primary-second">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <InfoSection
                    title={title}
                    details={details}
                />
                <VerificationStats
                    details={details}
                    verificationCount={verificationCount}
                    documentsCount={documents.length}
                />
                <AttachedDocuments documents={documents} />
            </div>

            {/* Approve / reject hidden from view
            {details.approval_status === "PENDING" && (
                <Can action={CHANGE_REQUEST_ACTIONS.approve}>
                    <div className="my-3 border-t border-primary-first" />
                    <div className="flex items-center gap-4">
                        <button
                            type="button"
                            disabled={loadingAction}
                            onClick={onReject}
                            className="px-4 py-1.5 text-[14px] font-medium rounded-[10px] bg-neutral-second text-neutral-first/50"
                        >
                            {t('reject_change')}
                        </button>

                        <button
                            type="button"
                            disabled={loadingAction}
                            onClick={onApprove}
                            className="px-4 py-1.5 text-[14px] font-medium rounded-[10px] bg-neutral-first text-neutral-second"
                        >
                            {t('approve_change')}
                        </button>
                    </div>
                </Can>
            )}
            */}
        </div>
    );
};
const InfoSection = ({
    title,
    details,
}: {
    title: string;
    details: ChangeRequest;
}) => {
    const t = useTranslations();
    return (
        <div className="space-y-2 text-[16px] text-neutral-first/50">
            <h3 className="text-[24px] font-medium text-neutral-first truncate" title={title}>{title}</h3>
            <div className="flex w-full overflow-hidden">
                <span className="w-1/2 truncate" title={t('change_id')}>{t('change_id')}:</span>
                <span className="w-1/2 pl-4 text-neutral-first font-medium truncate" title={details.change_request_id}>
                    <PrivateIdentifier value={details.change_request_id}/>
                </span>
            </div>
            <div className="flex w-full overflow-hidden">
                <span className="w-1/2 truncate" title={t("status")}>{t("status")}:</span>
                <span className={`w-1/2 pl-4 font-medium truncate ${statusClassMap[details.approval_status] ?? "text-neutral-first/50"}`} title={details.approval_status}>
                    <WorkflowStatus approval={details.approval_status} summary={details.awe_request_status_summary}/>
                </span>
            </div>
            <div className="flex w-full overflow-hidden">
                <span className="w-1/2 truncate" title={t("change_date")}>{t("change_date")}:</span>
                <span className="w-1/2 pl-4 text-neutral-first font-medium truncate" title={new Date(details.created_at).toLocaleDateString()}>
                    {new Date(details.created_at).toLocaleDateString()}
                </span>
            </div>
        </div>
    )
};

const VerificationStats = ({
    details,
    verificationCount,
    documentsCount,
}: {
    details: ChangeRequest;
    verificationCount: number;
    documentsCount: number;
}) => {
    const t = useTranslations();

    return (
        <div className="space-y-2 text-[16px] text-neutral-first/50">
            <h3 className="text-lg font-semibold text-neutral-first invisible">
                Verification
            </h3>

            <div className="border-l border-primary-first pl-6 space-y-2">
                <div className="flex w-full overflow-hidden">
                    <span className="w-1/2 truncate" title={t('documents_attached')}>{t('documents_attached')}:</span>
                    <span className="w-1/2 pl-4 text-neutral-first font-medium truncate" title={documentsCount.toString()}>
                        {documentsCount}
                    </span>
                </div>

                <div className="invisible flex w-full overflow-hidden" aria-hidden>
                    <span className="w-1/2 truncate" title={t('verifications_required')}>{t('verifications_required')}:</span>
                    <span className="w-1/2 pl-4 text-neutral-first font-medium truncate" title={details.no_of_verifications_required?.toString()}>
                        {details.no_of_verifications_required}
                    </span>
                </div>

                <div className="invisible flex w-full overflow-hidden" aria-hidden>
                    <span className="w-1/2 truncate" title={t('verifications_done')}>{t('verifications_done')}:</span>
                    <span className="w-1/2 pl-4 text-neutral-first font-medium truncate" title={verificationCount.toString()}>
                        {verificationCount}
                    </span>
                </div>
            </div>
        </div>
    );
};

const AttachedDocuments = ({ documents = [] }: { documents?: ChangeRequestDocument[] }) => {
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
                    alt="doc"
                    width={14}
                    height={14}
                    className="ml-1 mb-1"
                />
            </div>

            <div className="border-l border-primary-first pl-6 flex flex-col gap-2 font-semibold">
                {visibleDocs.map((doc, index) => (
                    <span
                        key={index}
                        onClick={() => window.open(doc.document_url, '_blank', 'noopener,noreferrer')}
                        className="flex items-center gap-2 cursor-pointer"
                    >
                        {doc.document_label}
                        <Image src="/images/common/arrow_next_01.png" alt="arrow" width={14} height={14} />
                    </span>
                ))}

                {Array.from({ length: placeholdersCount }).map((_, i) => (
                    <span key={i} className="invisible">placeholder</span>
                ))}
            </div>
        </div>
    );
};
