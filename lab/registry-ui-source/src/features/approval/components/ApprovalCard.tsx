'use client';

import { useState } from 'react';
import Image from 'next/image';
import { useTranslations } from 'next-intl';
import { ApprovalTask } from '@/features/approval/types/approval';
import { formatDateTime } from '@/shared/utils/dateUtils';
import { useAuth } from '@/context/Authcontext';
import { useRbac } from '@/context/RbacContext';
import { VERIFICATION_CHANGE_REQUEST_ACTIONS } from '@/features/change-request/utils/verificationChangeRequest.actions';
import { VERIFICATION_INTAKE_FORM_ACTIONS } from '@/features/intake-form/utils/verificationIntakeForm.actions';

interface Props {
    task: ApprovalTask;
    isPending: boolean;
    approvalDecisionBlocked?: boolean;
    onSubmit: (taskId: string, action: 'approve' | 'reject' | 'return', comment: string) => Promise<boolean>;
    intakeForm?: boolean;
}

export default function ApprovalCard({
    task,
    isPending,
    approvalDecisionBlocked = false,
    onSubmit,
    intakeForm = false,
}: Props) {
    const t = useTranslations();
    const { user } = useAuth();
    const { can } = useRbac();
    const canAct = can(
        intakeForm
            ? VERIFICATION_INTAKE_FORM_ACTIONS.create
            : VERIFICATION_CHANGE_REQUEST_ACTIONS.create,
    );
    const [comment, setComment] = useState('');
    const [reasonError,setReasonError] = useState('');
    const [submittingAction, setSubmittingAction] = useState<'approve' | 'reject' | 'return' | null>(null);

    const isCurrentUser = Boolean(user?.preferred_username && task.assignee === user.preferred_username);
    const assigneeDisplay = isCurrentUser ? user.name : task.assignee;

    const isTaskActionable = task.status === 'open' || task.status === 'claimed';
    const showActionForm = isPending && canAct && isCurrentUser && isTaskActionable && !approvalDecisionBlocked;
    const isInteractionDisabled = approvalDecisionBlocked || submittingAction !== null;

    const hasDecision = Boolean(task.decision_action);
    const decisionApproved = task.decision_action === 'approve';
    const displayDate = task.completed_at || task.created_at;

    const handleAction = async (action: 'approve' | 'reject' | 'return') => {
        if (action !== 'approve' && !comment.trim()) { setReasonError('Enter a reason before returning or rejecting this record.'); return; }
        setReasonError('');
        setSubmittingAction(action);
        const success = await onSubmit(task.id, action, comment);
        if (success) {
            setComment('');
        }
        setSubmittingAction(null);
    };

    return (
        <div className="registry-approval-card bg-secondary-second rounded-[10px] p-6 space-y-3">
            <div className="font-normal text-[14px] text-neutral-first/50">{t('assigned_to')}</div>

            <div className="flex items-center gap-3">
                <div className="w-10 h-10 relative">
                    <Image
                        src="/images/common/verified_person.png"
                        alt="approver"
                        fill
                        className="rounded-full object-cover"
                    />
                </div>
                <div className="flex flex-col">
                    <span className="text-[20px] font-medium text-neutral-first">
                        {assigneeDisplay}
                        {isCurrentUser && (
                            <span className="ml-2 text-[14px] text-neutral-first/50">{t('you')}</span>
                        )}
                    </span>
                    <span className="text-[14px] text-neutral-first/50 font-normal">
                        {formatDateTime(displayDate)}
                    </span>
                </div>
            </div>

            <div className="flex justify-between pr-10">
                <div>
                    <div className="text-[14px] font-normal text-neutral-first/50 mb-1">{t('stage')}</div>
                    <div className="text-[16px] text-neutral-first font-normal">
                        {task.stage_order}
                    </div>
                </div>

                <div>
                    <div className="text-[14px] font-normal text-neutral-first/50 mb-1">{t('status')}</div>
                    <div className="text-[16px] text-neutral-first font-normal capitalize">{task.status}</div>
                </div>
            </div>

            {showActionForm ? (
                <>
                    <div>
                        <div className="text-[14px] font-medium text-neutral-first/50 mb-1">{t('message')}</div>
                        <textarea
                            value={comment}
                            onChange={(e) => setComment(e.target.value)}
                            rows={2}
                            placeholder={t('type_your_message')}
                            disabled={isInteractionDisabled}
                            readOnly={approvalDecisionBlocked}
                            className="w-full border border-black/25 rounded-[10px] p-2 text-sm resize-none focus:outline-none bg-white disabled:bg-white disabled:opacity-50 disabled:cursor-not-allowed"
                        />
                    </div>

                    {reasonError && <p role="alert" className="text-red-700 text-sm">{reasonError}</p>}
                    <div className="registry-approval-actions flex flex-wrap items-center gap-3 pt-2">
                        <button type="button" disabled={isInteractionDisabled} onClick={() => handleAction('return')} className="rounded-full px-4 py-2 text-sm font-medium bg-amber-100 text-amber-900 disabled:opacity-50">{submittingAction === 'return' ? t('loading') : 'Return for correction'}</button>
                        <button
                            type="button"
                            disabled={isInteractionDisabled}
                            onClick={() => handleAction('reject')}
                            className="px-4 py-1.5 text-[14px] font-medium rounded-[10px] bg-neutral-second text-neutral-first/50 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {submittingAction === 'reject' ? t('loading') : 'Reject permanently'}
                        </button>
                        <button
                            type="button"
                            disabled={isInteractionDisabled}
                            onClick={() => handleAction('approve')}
                            className="px-4 py-1.5 text-[14px] font-medium rounded-[10px] bg-neutral-first text-neutral-second disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {submittingAction === 'approve' ? t('loading') : t('approve')}
                        </button>
                    </div>
                </>
            ) : (
                <>
                    {(task.decision_comment || hasDecision) && (
                        <div>
                            <div className="text-[14px] font-normal text-neutral-first/50 mb-1">
                                {t('message')}
                            </div>
                            <div className="text-[16px] text-neutral-first font-normal whitespace-pre-wrap">
                                {task.decision_comment?.trim() || '—'}
                            </div>
                        </div>
                    )}

                    {hasDecision && (
                        <div>
                            <div className="text-[14px] font-normal text-neutral-first/50 mb-1">
                                {t('action')}
                            </div>
                            <div
                                className={`text-[16px] font-medium ${
                                    decisionApproved ? 'text-toast-success' : 'text-toast-failed'
                                }`}
                            >
                                {task.decision_action === 'return' ? 'Returned for correction' : decisionApproved ? t('approve') : 'Rejected permanently'}
                            </div>
                        </div>
                    )}
                </>
            )}
        </div>
    );
}
