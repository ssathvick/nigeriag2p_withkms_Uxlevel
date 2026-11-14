'use client';

import { useTranslations } from 'next-intl';
import TasksListView from '@/features/approval/components/TasksListView';

export default function ChangeRequestTasksPage() {
    const t = useTranslations();

    return (
        <TasksListView
            fixedArtifactFilter="change_request"
            listBasePath="/tasks/change-request"
            breadcrumb={[
                { label: t('tasks') },
                { label: t('tasks_cr') },
            ]}
        />
    );
}
