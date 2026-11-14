'use client';

import { useTranslations } from 'next-intl';
import ApprovalCard from '@/features/approval/components/ApprovalCard';
import { useApprovals, ApprovalArtifactContext } from '@/features/approval/hooks/useApprovals';
import { VERIFICATION_INTAKE_FORM_ACTIONS } from '@/features/intake-form/utils/verificationIntakeForm.actions';
import Can from '@/components/shared/Can';
import ApprovalListSkeleton from '@/features/approval/components/ApprovalListSkeleton';

interface Props {
    awe_request_id?: string | null;
    artifactContext?: ApprovalArtifactContext | null;
    isPending: boolean;
    onRefresh?: () => void | Promise<void>;
}

export default function IntakeApprovalCard({
    awe_request_id,
    artifactContext,
    isPending,
    onRefresh,
}: Props) {
    const t = useTranslations();
    const { tasks, loadingTasks, submitDecision } = useApprovals(
        awe_request_id,
        artifactContext,
        onRefresh,
    );

    if (awe_request_id && loadingTasks) {
        return <ApprovalListSkeleton />;
    }

    return (
        <Can action={VERIFICATION_INTAKE_FORM_ACTIONS.view}>
            <div className="rounded-lg space-y-4">
                <div className="bg-primary-first px-6 py-4 rounded-[10px] flex justify-between items-center shadow-sm">
                    <h4 className="text-[24px] font-semibold text-neutral-first">{t('approvals')}</h4>
                </div>

                <div className="space-y-3">
                    {tasks.length === 0 ? (
                        <div className="py-4 text-center text-neutral-first/50 text-sm">
                            {t('no_approval_tasks')}
                        </div>
                    ) : (
                        tasks.map((task) => (
                            <ApprovalCard
                                key={task.id}
                                task={task}
                                isPending={isPending}
                                intakeForm
                                onSubmit={submitDecision}
                            />
                        ))
                    )}
                </div>
            </div>
        </Can>
    );
}
