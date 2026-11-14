'use client';

import { useMemo } from 'react';
import { useRouter } from '@/i18n/navigation';
import { useTranslations } from 'next-intl';
import { useRegister } from '@/context/RegisterContext';
import { ApprovalTask } from '@/features/approval/types/approval';
import { getTaskDetailHref } from '@/features/approval/utils/taskNavigation';
import TaskCard from '@/features/approval/components/TaskCard';

interface Props {
    tasks: ApprovalTask[];
}

export default function MyTasksList({ tasks }: Props) {
    const t = useTranslations();
    const router = useRouter();
    const { registers } = useRegister();

    const registerMnemonicById = useMemo(
        () => new Map(registers.map((r) => [r.register_id, r.register_mnemonic.toLowerCase()])),
        [registers],
    );

    if (tasks.length === 0) {
        return (
            <div className="text-sm text-secondary-third text-center py-6">
                {t('no_approval_tasks')}
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {tasks.map((task, index) => {
                const href = getTaskDetailHref(task, registerMnemonicById);

                return (
                    <TaskCard
                        key={task.id}
                        task={task}
                        index={index}
                        href={href}
                        onNavigate={(path) => router.push(path)}
                    />
                );
            })}
        </div>
    );
}
