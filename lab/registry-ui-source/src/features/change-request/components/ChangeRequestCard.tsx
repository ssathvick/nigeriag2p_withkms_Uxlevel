'use client';

import Image from "next/image";
import { useTranslations } from 'next-intl';
import { KeyValue } from '@/components/ui/KeyValue';
import { ChangeRequest } from "@/features/change-request/types";
import { useChangeRequestDocuments } from "../hooks/useChangeRequestDocuments";

interface Props {
    changeRequest: ChangeRequest;
    index: number;
    onViewDetails: () => void;
}

const statusClassMap: Record<string, string> = {
    REJECTED: "text-toast-failed",
    PENDING: "text-amber-500",
    APPROVED: "text-toast-success",
};

export default function ChangeRequestCard({
    changeRequest,
    index,
    onViewDetails,
}: Props) {

    const t = useTranslations();

    const { documents } =
        useChangeRequestDocuments(changeRequest.change_request_id);

    return (
        <div
            key={index}
            className="rounded-[10px] bg-neutral-second px-10 py-5"
        >
            <div className="mb-4 flex items-start justify-between gap-6">
                <h3
                    className="min-w-0 flex-1 text-[20px] font-semibold leading-snug tracking-tight text-neutral-first line-clamp-2 md:text-[22px]"
                    title={changeRequest.record_name?.trim() || undefined}
                >
                    {changeRequest.record_name?.trim() || '—'}
                </h3>
                <h3
                    className="min-w-0 flex-1 text-right text-[20px] font-semibold leading-snug tracking-tight text-neutral-first line-clamp-2 md:text-[22px]"
                    title={changeRequest.section_mnemonic?.trim() || undefined}
                >
                    {changeRequest.section_mnemonic?.trim() || '—'}
                </h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 items-stretch gap-6 text-[16px] text-neutral-first/50">
                <div className="flex h-full min-h-0 flex-col">
                    <div className="flex flex-1 flex-col space-y-2">
                        <KeyValue label={t('change_request_id')} value={'•••'+changeRequest.change_request_id.slice(-3)} />
                        <KeyValue
                            label={t('change_date')}
                            value={new Date(changeRequest.created_at).toLocaleDateString()}
                        />
                        <KeyValue label={t('register')} value={changeRequest.register_mnemonic?.trim() || '—'} />
                    </div>
                </div>

                <div className="flex h-full min-h-0 flex-col">
                    <div className="flex flex-1 flex-col space-y-2 border-l-2 border-secondary-second pl-6">
                        <KeyValue
                            label={t('documents_attached')}
                            value={documents.length.toString()}
                        />
                        <div className="invisible" aria-hidden>
                            <KeyValue
                                label={t('verifications_required')}
                                value="—"
                            />
                        </div>
                        <div className="invisible" aria-hidden>
                            <KeyValue
                                label={t('verifications_done')}
                                value="—"
                            />
                        </div>
                    </div>
                </div>

                <div className="flex h-full min-h-0 flex-col">
                    <div className="flex flex-1 flex-col space-y-2 border-l-2 border-secondary-second pl-6">
                        <KeyValue
                            label={t('approval_status')}
                            value={changeRequest.approval_status}
                            valueClassName={
                                statusClassMap[changeRequest.approval_status] ?? 'text-neutral-first/50'
                            }
                        />
                        <KeyValue
                            label={t('approved_by')}
                            value={changeRequest.approved_by?.trim() || '—'}
                        />
                        <KeyValue
                            label={t('approved_at')}
                            value={
                                changeRequest.approved_at
                                    ? new Date(changeRequest.approved_at).toLocaleString()
                                    : '—'
                            }
                        />
                    </div>
                </div>

                <div className="flex h-full min-h-0 flex-col">
                    <div className="flex flex-1 flex-col space-y-2 border-l-2 border-secondary-second pl-6">
                        <div className="flex items-center gap-1 leading-none">
                            <span className="text-[16px] font-medium text-neutral-first">
                                {t('attached_documents')}
                            </span>
                            <Image
                                src="/images/changerequest/attached_doc_icon.png"
                                alt=""
                                width={14}
                                height={14}
                                className="mb-0.5 ml-0.5"
                            />
                        </div>
                        <div className="flex flex-col gap-2 font-normal text-[16px] text-neutral-first/50">
                            {documents.slice(0, 3).map((doc, docIndex) => (
                                <span
                                    key={doc.document_url ?? docIndex}
                                    onClick={() => window.open(doc.document_url, '_blank', 'noopener,noreferrer')}
                                    className="flex cursor-pointer items-center gap-2"
                                >
                                    {doc.document_label}
                                    <Image
                                        src="/images/common/arrow_next_01.png"
                                        alt=""
                                        width={14}
                                        height={14}
                                    />
                                </span>
                            ))}
                            {Array.from({ length: Math.max(0, 3 - documents.length) }).map((_, idx) => (
                                <span
                                    key={`placeholder-${idx}`}
                                    className="invisible flex items-center gap-2"
                                    aria-hidden
                                >
                                    placeholder
                                </span>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            <div className="my-4 border-t border-secondary-second" />

            <div className="flex items-center justify-between">
                <button
                    type="button"
                    onClick={onViewDetails}
                    className="flex items-center gap-2 text-[14px] font-normal text-neutral-first opacity-60 transition hover:opacity-100"
                >
                    {t('view_details')}
                    <Image
                        src="/images/common/arrow_next_01.png"
                        alt=""
                        width={14}
                        height={14}
                    />
                </button>
            </div>
        </div>
    );
}
