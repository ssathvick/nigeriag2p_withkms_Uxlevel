'use client';

import { useMemo } from 'react';
import { useParams } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { ChangeRequestDetailsView } from '@/features/change-request/components';

export default function TaskChangeRequestDetailPage() {
    const t = useTranslations();
    const { changeId } = useParams<{ changeId: string }>();

    const breadcrumb = useMemo(
        () => [
            { label: t('tasks'), href: '/tasks/change-request' },
            { label: t('tasks_cr') },
            { label: t('change_id_breadcrumb', { id: '•••'+changeId.slice(-3) }) },
        ],
        [changeId, t],
    );

    return <ChangeRequestDetailsView changeId={changeId} breadcrumb={breadcrumb} />;
}
