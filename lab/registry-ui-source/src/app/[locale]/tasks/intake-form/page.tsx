'use client';

import { useTranslations } from 'next-intl';
import TasksListView from '@/features/approval/components/TasksListView';

export default function IntakeFormTasksPage() {
    const t = useTranslations();

    return (
        <TasksListView
            fixedArtifactFilter="intake_form"
            listBasePath="/tasks/intake-form"
            breadcrumb={[
                { label: t('tasks') },
                { label: t('tasks_intake') },
            ]}
        />
    );
}
