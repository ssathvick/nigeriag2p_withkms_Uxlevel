'use client';

import Image from 'next/image';
import { useTranslations } from 'next-intl';
import { ApprovalTask } from '@/features/approval/types/approval';
import { formatDateTime } from '@/shared/utils/dateUtils';
import {
    REGISTRY_CHANGE_REQUEST_ARTIFACT,
    REGISTRY_INTAKE_FORM_ARTIFACT,
} from '@/features/approval/constants';

interface Props {
    task: ApprovalTask;
    index: number;
    href: string | null;
    onNavigate: (href: string) => void;
}

const taskStatusClassMap: Record<string, string> = {
    open: 'text-amber-500',
    claimed: 'text-amber-500',
    completed: 'text-toast-success',
    cancelled: 'text-toast-failed',
};

function KeyValue({ label, value }: { label: string; value: string }) {
    return (
        <div className="flex w-full text-neutral-first leading-relaxed overflow-hidden">
            <span
                className="w-1/2 font-normal text-neutral-first/50 text-[16px] truncate"
                title={label}
            >
                {label}:
            </span>
            <span className="w-1/2 font-medium text-[14px] truncate pl-4" title={value}>
                {value}
            </span>
        </div>
    );
}

function getContextString(context: Record<string, unknown> | null | undefined, key: string): string {
    const value = context?.[key];
    if (value === null || value === undefined || value === '') return '—';
    return String(value);
}

export default function TaskCard({ task, index, href, onNavigate }: Props) {
    const t = useTranslations();
    const context = task.context ?? {};
    const isIntake = task.artifact_type === REGISTRY_INTAKE_FORM_ARTIFACT;
    const isChangeRequest = task.artifact_type === REGISTRY_CHANGE_REQUEST_ARTIFACT;

    const recordName = getContextString(context, 'record_name');
    const registerMnemonic = getContextString(context, 'register_mnemonic');
    const mnemonicKey = isIntake ? 'intake_form_mnemonic' : 'section_mnemonic';
    const mnemonicLabel = isIntake ? t('intake_form_mnemonic') : t('section_mnemonic');
    const mnemonicRaw = getContextString(context, mnemonicKey);
    const mnemonicDisplay =
        mnemonicRaw === '—' ? mnemonicRaw : t(mnemonicRaw, { default: mnemonicRaw });

    const displayName =
        recordName !== '—'
            ? recordName
            : isIntake
              ? t('intake_submission')
              : t('change_request_fallback', { index: index + 1 });

    const artifactId = isIntake
        ? getContextString(context, 'submission_id') || task.artifact_id || '—'
        : getContextString(context, 'change_request_id') || task.artifact_id || '—';

    const statusClass = taskStatusClassMap[task.status.toLowerCase()] ?? 'text-neutral-first/50';

    const handleViewDetails = () => {
        if (href) onNavigate(href);
    };

    return (
        <div
            className={`rounded-[10px] bg-neutral-second px-10 ${isIntake ? 'py-8' : 'py-5'}`}
        >
            <h3
                className="text-[24px] font-medium text-neutral-first truncate mb-6"
                title={displayName}
            >
                {displayName}
            </h3>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 divide-x divide-secondary-second">
                <div className="space-y-2 pr-6 text-[16px] text-neutral-first/50">
                    {isIntake && (
                        <KeyValue label={t('submission_id')} value={getContextString(context, 'application_reference') || '•••'+artifactId.slice(-3)} />
                    )}

                    {isChangeRequest && (
                        <KeyValue label={t('change_id')} value={getContextString(context, 'application_reference') || '•••'+artifactId.slice(-3)} />
                    )}

                    <KeyValue label={t('register_mnemonic')} value={registerMnemonic} />

                    <div className="flex w-full overflow-hidden">
                        <span className="w-1/2 truncate" title={t('status')}>
                            {t('status')}:
                        </span>
                        <span
                            className={`w-1/2 pl-4 font-medium truncate capitalize ${statusClass}`}
                            title={task.status}
                        >
                            {task.status}
                        </span>
                    </div>
                </div>

                <div className="space-y-2 px-6 text-[16px] text-neutral-first/50">
                    <KeyValue label={mnemonicLabel} value={mnemonicDisplay} />
                    <KeyValue label={t('stage')} value={String(task.stage_order)} />
                    {task.kind && (
                        <KeyValue label={t('kind', { default: 'Kind' })} value={task.kind} />
                    )}
                </div>

                <div className="space-y-2 pl-6 text-[16px] text-neutral-first/50">
                    <div className="flex w-full overflow-hidden">
                        <span className="w-1/2 truncate" title={t('created_at')}>
                            {t('created_at')}:
                        </span>
                        <span
                            className="w-1/2 pl-4 text-neutral-first font-medium truncate"
                            title={formatDateTime(task.created_at)}
                        >
                            {formatDateTime(task.created_at)}
                        </span>
                    </div>

                    {task.due_at && (
                        <div className="flex w-full overflow-hidden">
                            <span className="w-1/2 truncate" title={t('due_at', { default: 'Due At' })}>
                                {t('due_at', { default: 'Due At' })}:
                            </span>
                            <span
                                className="w-1/2 pl-4 text-neutral-first font-medium truncate"
                                title={formatDateTime(task.due_at)}
                            >
                                {formatDateTime(task.due_at)}
                            </span>
                        </div>
                    )}

                    {task.completed_at && (
                        <div className="flex w-full overflow-hidden">
                            <span className="w-1/2 truncate" title={t('completed_at')}>
                                {t('completed_at')}:
                            </span>
                            <span
                                className="w-1/2 pl-4 text-neutral-first font-medium truncate"
                                title={formatDateTime(task.completed_at)}
                            >
                                {formatDateTime(task.completed_at)}
                            </span>
                        </div>
                    )}
                </div>
            </div>

            <div className="my-4 border-t border-secondary-second" />

            <div className="flex items-center justify-between">
                {href&&<button
                    type="button"
                    onClick={handleViewDetails}
                    className="text-[14px] text-neutral-first font-normal flex items-center gap-2 opacity-60 hover:opacity-100 transition disabled:cursor-default disabled:opacity-40"
                >
                    {t('view_details')}
                    <Image
                        src="/images/common/arrow_next_01.png"
                        alt="arrow"
                        width={14}
                        height={14}
                    />
                </button>}
            </div>
        </div>
    );
}
