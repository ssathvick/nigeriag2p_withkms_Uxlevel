'use client';

import Image from 'next/image';
import { useState } from 'react';
import { KeyValue } from '@/components/ui/KeyValue';
import { OutgoingMessage } from '../types';
import Link from 'next/link';
import { useTranslations } from 'next-intl';
import { formatDateTime } from '@/shared/utils/dateUtils';

interface Props {
    message: OutgoingMessage;
}

export default function OutgoingMessageCard({ message }: Props) {
    const t = useTranslations();
    const [showAllTopics, setShowAllTopics] = useState(false);


    const topicsToShow = showAllTopics ? message.topic_names : message.topic_names.slice(0, 4);

    return (
        <div className="application-message-card rounded-[10px] bg-neutral-second px-10 py-8">
            <div className="grid gap-6 grid-cols-1 md:grid-cols-3 text-[16px] text-neutral-first/50">

                <div className="space-y-2">
                    <h3 className="text-[16px] font-medium text-primary-second flex justify-between items-center">
                        <span>{t('source') || 'Source'}</span>
                    </h3>
                    <KeyValue variant="message" label={t('outgest_id') || 'Outgest ID'} value={message.outgest_id} />
                    <KeyValue variant="message" label={t('queued_date_time') || 'Queued Date & Time'} value={formatDateTime(message.queued_datetime)} />
                    <KeyValue variant="message" label={t('source_register') || 'Source Register'} value={message.source_register} />
                    <KeyValue variant="message" label={t('record_id') || 'Record ID'} value={message.record_id} />
                    <KeyValue variant="message" label={t('source_change_request_id') || 'Source Change Request ID'} value={message.source_change_request_id} />
                </div>

                <div className="border-l-2 border-secondary-second pl-6 flex flex-col justify-between">
                    <div className='space-y-2'>
                        <h3 className="text-[16px] font-medium text-primary-second">{t('topic_resolution_status') || 'Topic Resolution Status'}</h3>
                        <KeyValue variant="message" label={t('topic_resolution') || 'Topic Resolution'} value={message.topic_resolution} />
                        <KeyValue variant="message" label={t('date_and_time') || 'Date & Time'} value={formatDateTime(message.topic_resolution_datetime)} />
                    </div>
                    <div className='space-y-2'>
                        <h3 className="text-[16px] font-medium text-primary-second">{t('topics') || 'Topics'}</h3>
                        <KeyValue variant="message" label={t('number_of_topics_resolved') || 'Number of Topics Resolved'} value={message.number_of_topics_resolved.toString()} />
                    </div>
                </div>


                <div className="border-l-2 border-secondary-second pl-6 space-y-2">
                    <h3 className="text-[16px] font-medium text-primary-second">{t('topic_names') || 'Topic Names'}</h3>
                    {topicsToShow.map((topic, idx) => (
                        <KeyValue variant="message" key={idx} label={`${t('topic') || 'Topic'} ${idx + 1}`} value={topic} />
                    ))}
                    {message.topic_names.length > 4 && !showAllTopics && (
                        <button type="button" onClick={()=>setShowAllTopics(true)}
                            className="text-neutral-first/50 inline-flex items-center gap-1"
                        >
                            {t('view_more') || "View More"}
                            <Image
                                src="/images/common/arrow_next_01.png"
                                alt="Arrow"
                                width={14}
                                height={14}
                                className="inline-block"
                            />
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
}
