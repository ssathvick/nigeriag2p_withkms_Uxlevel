'use client';

import { TopBar } from '@/components/shared';
import { useTranslations } from 'next-intl';
import { useRegister } from '@/context/RegisterContext';
import { useParams, useSearchParams } from 'next/navigation';
import { useState,useEffect } from 'react';
import { WorkflowFilters } from '@/components/shared/Workflow';

import IntakeFormSubmissionList from '@/features/intake-form/components/SubmissionList';
import { usePagination } from '@/shared/hooks';
import { STATIC_INPUT_MECHANISMS } from '@/features/intake-form/constants/inputMechanisms';
import { useIntakeSubmissions } from '@/features/intake-form/hooks/useIntakeSubmissions';
import { INTAKE_FORM_ACTIONS } from '@/features/intake-form/utils/intakeForm.actions';
import Can from '@/components/shared/Can';
import { useRuntimeConfig } from '@/context/RuntimeConfigContext';
import AddNewDropdown from '@/components/ui/AddNewDropdown';

export default function IntakeFormPage() {
    const t = useTranslations();
    const { config } = useRuntimeConfig();

    const routeParams = useParams<{ type: string }>();
    const registerType = routeParams.type;

    const searchParams = useSearchParams();
    const [searchQuery, setSearchQuery] = useState(searchParams.get('search') || '');
    const [currentPage, setCurrentPage] = useState(1);
    useEffect(()=>setCurrentPage(1),[searchParams.get("status")]);
    const pageSize = config?.pageSize || 10;

    const { currentRegister } = useRegister();
    const registerId = currentRegister?.register_id;

    const mechanisms = STATIC_INPUT_MECHANISMS.map(({ labelKey, ...mechanism }) => ({
        ...mechanism,
        display_key: t(labelKey),
    }));

    const { submissions, paginationInfo, loading: submissionsLoading } = useIntakeSubmissions(registerId,
        {
            searchText: searchQuery,
            status: searchParams.get("status") || "all",
            currentPage,
            pageSize,
        });

    const pagination = usePagination({
        totalItems: paginationInfo?.number_of_items ?? 0,
        currentPage,
        pageSize,
        currentCount: submissions?.length || 0,
    });

    const handleSearch = (newSearchQuery: string) => {
        setSearchQuery(newSearchQuery);
        setCurrentPage(1);
    };

    const handlePreviousPage = () => {
        setCurrentPage(prev => Math.max(prev - 1, 1));
    };

    const handleNextPage = () => {
        setCurrentPage(prev => prev + 1);
    };

    return (
        <div className="min-h-screen mx-auto bg-secondary-first">
            <TopBar
                breadcrumb={[{ label: t("register_intake_form", { subject: currentRegister?.register_subject || t("register") }) }]}
                showFilters={false}
                showPagination
                showCapsule={true}
                capsule={
                    <Can action={INTAKE_FORM_ACTIONS.edit}>
                        <AddNewDropdown mechanisms={mechanisms} />
                    </Can>
                }
                pageStart={pagination.pageStart}
                pageEnd={pagination.pageEnd}
                total={pagination.total}
                onPrev={handlePreviousPage}
                onNext={handleNextPage}
                showSearch
                searchValue={searchQuery || ''}
                searchPlaceholder={t('search')}
                onSearch={handleSearch}
            />

            <WorkflowFilters draft />
            <div className="px-7.5">
                {submissionsLoading ? (
                    <div className="space-y-4">
                        {[...Array(3)].map((_, i) => (
                            <div key={i} className="rounded-[10px] bg-neutral-second px-10 py-8 animate-pulse">
                                <div className="grid gap-6 grid-cols-1 md:grid-cols-4">
                                    {[...Array(4)].map((_, j) => (
                                        <div key={j} className="space-y-3">
                                            <div className="h-5 bg-secondary-second rounded w-24" />
                                            <div className="h-4 bg-secondary-first rounded w-full" />
                                            <div className="h-4 bg-secondary-first rounded w-3/4" />
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                ) : submissions && submissions.length > 0 ? (
                    <IntakeFormSubmissionList
                        submissions={submissions}
                        registerType={registerType}
                    />
                ) : (
                    <div className="text-sm text-secondary-third text-center py-6">
                        {t('no_submissions')}
                    </div>
                )}
            </div>
            <div className='h-15'>&nbsp;</div>
        </div>
    );
}
