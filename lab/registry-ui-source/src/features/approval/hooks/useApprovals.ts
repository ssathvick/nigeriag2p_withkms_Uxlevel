import { useState, useEffect, useCallback, useMemo } from 'react';
import { useFetch } from '@/shared/hooks/useFetch';
import { toast } from 'react-toastify';
import { useTranslations } from 'next-intl';
import { ApprovalTask } from '@/features/approval/types/approval';

export interface ApprovalArtifactContext {
    artifactId: string;
    artifactType: string;
    currentStage: number;
}

export const useApprovals = (
    aweRequestId?: string | null,
    artifactContext?: ApprovalArtifactContext | null,
    onRefresh?: () => void | Promise<void>,
) => {
    const t = useTranslations();
    const [tasks, setTasks] = useState<ApprovalTask[]>([]);
    const [loadingTasks, setLoadingTasks] = useState(true);

    const fetchOptions = useMemo(
        () => ({
            method: 'POST' as const,
            body: JSON.stringify({
                request_id: aweRequestId,
            }),
        }),
        [aweRequestId],
    );

    const { data: tasksResp, loading: tasksLoading, execute: refetchTasks } = useFetch<{
        tasks: ApprovalTask[];
        total: number;
    }>({
        url: '/api/awe/tasks-for-request',
        enabled: !!aweRequestId,
        options: fetchOptions,
    });

    const { execute: executeDecision } = useFetch<{ decision: unknown }>({
        url: '/api/awe/submit-task-decision',
        enabled: false,
    });

    useEffect(() => {
        setTasks([]);
        if (!aweRequestId) {
            setLoadingTasks(false);
        }
    }, [aweRequestId]);

    useEffect(() => {
        if (!aweRequestId) return;
        if (tasksResp?.tasks) {
            setTasks(tasksResp.tasks);
        }
        setLoadingTasks(tasksLoading);
    }, [tasksResp, tasksLoading, aweRequestId]);

    const refreshApprovalState = useCallback(async () => {
        if (aweRequestId) {
            const refreshed = await refetchTasks('/api/awe/tasks-for-request', fetchOptions);
            if (refreshed?.tasks) {
                setTasks(refreshed.tasks);
            }
        }
        await onRefresh?.();
    }, [aweRequestId, refetchTasks, fetchOptions, onRefresh]);

    const submitDecision = useCallback(
        async (taskId: string, action: 'approve' | 'reject' | 'return', comment: string) => {
            if (!artifactContext) {
                toast.error(t('toast_approval_submit_failed'), { autoClose: 5000 });
                return false;
            }

            try {
                const result = (await executeDecision('/api/awe/submit-task-decision', {
                    method: 'POST',
                    body: JSON.stringify({
                        task_id: taskId,
                        action,
                        comment: comment || null,
                        artifact_id: artifactContext.artifactId,
                        artifact_type: artifactContext.artifactType,
                        current_stage: artifactContext.currentStage,
                    }),
                })) as { decision?: unknown; error?: string } | null;

                if (result && typeof result.error === 'string' && result.error.trim()) {
                    toast.error(t('toast_operation_error', { error: result.error }), {
                        position: 'top-right',
                        autoClose: 5000,
                    });
                    await refreshApprovalState();
                    return false;
                }

                if (result?.decision) {
                    toast.success(t('toast_approval_submitted'), {
                        position: 'top-right',
                        autoClose: 4000,
                    });
                    await refreshApprovalState();
                    return true;
                }

                toast.error(t('toast_approval_submit_failed'), {
                    autoClose: 5000,
                });
                await refreshApprovalState();
                return false;
            } catch {
                toast.error(t('toast_approval_submit_failed'), {
                    autoClose: 5000,
                });
                await refreshApprovalState();
                return false;
            }
        },
        [executeDecision, refreshApprovalState, artifactContext, t],
    );

    return { tasks, loadingTasks, submitDecision };
};
