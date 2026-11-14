'use client';

import { WorkflowFilters } from '@/components/shared/Workflow';
import { useCallback, useMemo } from 'react';
import { useSearchParams } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { useRouter } from '@/i18n/navigation';

import { TopBar } from '@/components/shared';
import MyTasksList from '@/features/approval/components/MyTasksList';
import { ChangeRequestSkeleton } from '@/features/change-request/components';
import { useMyTasks } from '@/features/approval/hooks/useMyTasks';
import { TASK_ARTIFACT_FILTER_OPTIONS } from '@/features/approval/constants';
import { useRuntimeConfig } from '@/context/RuntimeConfigContext';

export type TaskListArtifactFilter = 'change_request' | 'intake_form';

interface BreadcrumbItem {
    label: string;
    href?: string;
}

interface TasksListViewProps {
    fixedArtifactFilter?: TaskListArtifactFilter;
    breadcrumb: BreadcrumbItem[];
    listBasePath: string;
}

export default function TasksListView({
    fixedArtifactFilter,
    breadcrumb,
    listBasePath,
}: TasksListViewProps) {
    const t = useTranslations();
    const router = useRouter();
    const searchParams = useSearchParams();
    const { config } = useRuntimeConfig();

    const searchQuery = searchParams.get('search') || '';
    const artifactFilterParam = searchParams.get('artifact_type');

    const artifactType = useMemo(() => {
        const filter = fixedArtifactFilter ?? artifactFilterParam;
        if (!filter) return undefined;
        return TASK_ARTIFACT_FILTER_OPTIONS.find((o) => o.value === filter)?.artifactType;
    }, [fixedArtifactFilter, artifactFilterParam]);

    const pageSize = config.pageSize || 25;

    const { tasks, loading, total, currentPage, pages, setCurrentPage } = useMyTasks({
        artifactType,
        status: searchParams.get('status') || 'all',
        searchText: searchQuery,
        pageSize,
    });

    const handleSearch = useCallback(
        (searchValue: string) => {
            const params = new URLSearchParams(searchParams.toString());
            if (searchValue.trim()) {
                params.set('search', searchValue.trim());
            } else {
                params.delete('search');
            }
            params.set('page', '1');
            if (fixedArtifactFilter) {
                params.delete('artifact_type');
            }
            const query = params.toString();
            router.push(query ? `${listBasePath}?${query}` : listBasePath);
        },
        [router, searchParams, listBasePath, fixedArtifactFilter],
    );

    const pageStart = total === 0 ? 0 : (currentPage - 1) * pageSize + 1;
    const pageEnd = Math.min(currentPage * pageSize, total);

    return (
        <div className="min-h-screen mx-auto bg-secondary-first">
            <TopBar
                breadcrumb={breadcrumb}
                showSearch
                searchValue={searchQuery}
                searchPlaceholder={t('search_approval_tasks')}
                onSearch={handleSearch}
                pxClass="px-0.5"
                showFilters={false}
                showPagination
                pageStart={pageStart}
                pageEnd={pageEnd}
                total={total}
                onPrev={() => setCurrentPage((p) => Math.max(1, p - 1))}
                onNext={() => setCurrentPage((p) => Math.min(pages, p + 1))}
            />

            <WorkflowFilters tasks />
            <div className="px-7.5 pb-10">
                {loading ? (
                    <div className="space-y-4">
                        {[...Array(3)].map((_, i) => (
                            <ChangeRequestSkeleton key={i} />
                        ))}
                    </div>
                ) : (
                    <MyTasksList tasks={tasks} />
                )}
            </div>
        </div>
    );
}
