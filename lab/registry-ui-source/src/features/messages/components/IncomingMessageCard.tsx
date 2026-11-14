'use client';

import Image from 'next/image';
import { IncomingMessage } from '@/features/messages/types';
import { useState } from 'react';
import {useRbac} from '@/context/RbacContext';
import MessagePopup from './MessagePopup';
import { KeyValue } from '@/components/ui/KeyValue';
import { useTranslations, useLocale } from 'next-intl';
import { useIncomingMessagePayload } from '../hooks';
import { formatDateTime } from '@/shared/utils/dateUtils';

interface Props {
    message: IncomingMessage;
}

export default function IncomingMessageCard({ message }: Props) {
    const [openPopup, setOpenPopup] = useState(false);
    const locale = useLocale();
    const t = useTranslations();const {can}=useRbac();

    const {
        fetchAll,
        rawJson,
        transformedJson,
        enrichedJson,
        loading,
    } = useIncomingMessagePayload();


    return (
        <div className="application-message-card rounded-[10px] bg-neutral-second px-10 py-8">
            <div className="grid gap-6 grid-cols-1 md:grid-cols-4 text-[16px] text-neutral-first/50">
                {/* Column 1: Raw */}
                <div className="space-y-4">
                    <h3 className="text-[18px] font-semibold text-primary-second flex justify-between items-center">
                        <span>{t('raw') || 'Raw'}</span>
                        <Image
                            src="/images/messages/chat.png"
                            alt={t('raw') || 'Raw'}
                            width={19}
                            height={20}
                            onClick={() => {
                                fetchAll(message.ingest_id);
                                setOpenPopup(true);
                            }}
                            className="cursor-pointer" role="button" tabIndex={0} aria-label="View message details" onKeyDown={e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();fetchAll(message.ingest_id);setOpenPopup(true)}}}
                        />
                    </h3>

                    <div className="space-y-2">
                        <KeyValue label={t('ingest_id') || 'Ingest ID'} value={message.ingest_id} />
                        <KeyValue label={t('partner') || 'Partner'} value={message?.partner_mnemonic} />
                        <KeyValue label={t('data_model') || 'Data Model'} value={message?.data_model_mnemonic} />
                        <KeyValue label={t('date_and_time') || 'Date & Time'} value={formatDateTime(message.receipt_date_time)} />
                    </div>
                </div>

                {/* Column 2: Classification */}
                <div className="border-l-2 space-y-4 border-secondary-second pl-6">
                    <h3 className="text-[18px] font-semibold text-primary-second">{t('classification') || 'Classification'}</h3>
                    <div className="space-y-2">
                        <KeyValue label={t('status') || 'Status'} value={message.classification_status} />
                        <KeyValue label={t('date_and_time') || 'Date & Time'} value={formatDateTime(message.classification_date_time)} />
                        <KeyValue label={t('target_register') || 'Target Register'} value={message.register_mnemonic ?? '-- -- --'} />
                        <KeyValue label={t('target_section') || 'Target Section'} value={message.section_mnemonic ?? t('n_a') ?? 'N/A'} />
                        <KeyValue label={t('target_form') || 'Target Form'} value={message.intake_form_mnemonic ?? t('n_a') ?? 'N/A'} />
                    </div>
                </div>

                {/* Column 3: Transformation */}
                <div className="border-l-2 space-y-4 border-secondary-second pl-6">
                    <h3 className="text-[18px] font-semibold text-primary-second flex justify-between items-center">
                        <span>{t('transformation') || 'Transformation'}</span>
                        <Image
                            src="/images/messages/chat.png"
                            alt={t('transformation') || 'Transformation'}
                            width={19}
                            height={20}
                            onClick={() => {
                                fetchAll(message.ingest_id);
                                setOpenPopup(true);
                            }}
                            className="cursor-pointer" role="button" tabIndex={0} aria-label="View message details" onKeyDown={e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();fetchAll(message.ingest_id);setOpenPopup(true)}}}
                        />
                    </h3>

                    <div className="space-y-2">
                        <KeyValue label={t('status') || 'Status'} value={message.transformation_status ?? t('n_a') ?? 'N/A'} />
                        <KeyValue label={t('date_and_time') || 'Date & Time'} value={formatDateTime(message.transformation_date_time)} />
                        <KeyValue label={t('template') || 'Template'} value={message.template_file_id ?? t('n_a') ?? 'N/A'} />
                        <KeyValue label={t('pipeline_action') || 'Pipeline Action'} value={message.pipeline_action ?? t('n_a') ?? 'N/A'} />
                    </div>
                </div>

                {/* Column 4: Ingestion */}
                <div className="border-l-2 space-y-4 border-secondary-second pl-6">
                    <h3 className="text-[18px] font-semibold text-primary-second">{t('ingestion') || 'Ingestion'}</h3>
                    <div className="space-y-2">
                        <KeyValue label={t('status') || 'Status'} value={message.ingestion_status ?? t('n_a') ?? 'N/A'} />
                        <KeyValue label={t('date_and_time') || 'Date & Time'} value={formatDateTime(message.ingestion_date_time)} />
                        <KeyValue
                            label={t('form_submission_id') || 'Form Submission ID'}
                            value={message.intake_form_submission_id ?? t('n_a') ?? 'N/A'}
                            href={
                                message.intake_form_submission_id && message.register_mnemonic && can("intakeSubmission:view")
                                    ? `/${locale}/intake-form/${message.register_mnemonic.toLowerCase()}/submission/${message.intake_form_submission_id}`
                                    : undefined
                            }
                        />
                        <KeyValue
                            label={t('cr') || 'CR'}
                            value={message.change_request_id ?? t('n_a') ?? 'N/A'}
                            href={message.change_request_id && can("changeRequest:view") ? `/${locale}/incoming-messages/change-request/${message.change_request_id}` : undefined}
                        />
                    </div>
                </div>
            </div>
            {openPopup && (
                <MessagePopup
                    onClose={() => setOpenPopup(false)}
                    rawJson={rawJson}
                    transformedJson={transformedJson}
                    enrichedJson={enrichedJson}
                    loading={loading}
                />
            )}
        </div>
    );
}
