'use client';

import { useMemo, useState } from 'react';
import { TopBar, BreadcrumbBar } from '@/components/shared';
import { useParams } from 'next/navigation';
import {
    ConfigDetailsSummary,
    useAllRegister,
    useScoreDefinitions,
    getRegisterDetails,
} from '@/features/configuration/shared';
import ScoreContributingAttributesView from '@/features/configuration/registers/ScoreContributingAttributesView';
import EditScoreModal from '@/features/configuration/registers/EditScoreModal';
import ViewScoreDefinitionModal from '@/features/configuration/registers/ViewScoreDefinitionModal';
import { useBreadcrumb } from '@/shared/hooks/useBreadcrumb';
import { usePagination } from '@/shared/hooks/usePagination';
import { useRuntimeConfig } from '@/context/RuntimeConfigContext';
import { useRbac } from '@/context/RbacContext';
import { CONFIGURATION_TABS_ACTIONS } from '@/features/configuration/shared/utils/configurationTabs.actions';
import { useTranslations } from 'next-intl';

const ScoreDefinitionAttributesPage = () => {
    const t = useTranslations();
    const { registerId, scoreDefinitionId } = useParams<{
        registerId: string;
        scoreDefinitionId: string;
    }>();

    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isEditScoreModalOpen, setIsEditScoreModalOpen] = useState(false);
    const [isViewScoreModalOpen, setIsViewScoreModalOpen] = useState(false);
    const [currentPage, setCurrentPage] = useState(1);
    const { config } = useRuntimeConfig();
    const PAGE_SIZE = config.pageSize || 10;
    const [paginationInfo, setPaginationInfo] = useState({ totalItems: 0, currentCount: 0 });

    const { can } = useRbac();
    const canCreate = can(CONFIGURATION_TABS_ACTIONS.create);
    const canEditScore = can(CONFIGURATION_TABS_ACTIONS.edit);

    const { registers, loading: registersLoading } = useAllRegister(1, 100);
    const { scoreDefinitions, loading: scoresLoading, refresh: refreshScores } = useScoreDefinitions(
        registerId,
        1,
        500,
    );

    const pagination = usePagination({
        currentPage,
        pageSize: PAGE_SIZE,
        totalItems: paginationInfo.totalItems,
        currentCount: paginationInfo.currentCount,
    });

    const registerDetails = getRegisterDetails(registerId, registers);

    const scoreDetails = useMemo(
        () =>
            scoreDefinitions.find((s) => s.score_definition_id === scoreDefinitionId) ?? null,
        [scoreDefinitions, scoreDefinitionId],
    );

    const scoreLabel = scoreDetails?.score_type ?? scoreDefinitionId;

    const breadcrumb = useBreadcrumb({
        rootItem: { label: t('registers'), href: '/configuration/registers' },
        customItems: [
            {
                label: registerDetails.register_mnemonic || '',
                href: `/configuration/registers/${registerId}`,
            },
            {
                label: scoreLabel,
                href: `/configuration/registers/${registerId}/scores/${scoreDefinitionId}`,
            },
        ],
    });

    const handlePrev = () => {
        setCurrentPage((prev) => Math.max(1, prev - 1));
    };

    const handleNext = () => {
        if (currentPage * PAGE_SIZE < paginationInfo.totalItems) {
            setCurrentPage((prev) => prev + 1);
        }
    };

    if (registersLoading || scoresLoading) {
        return (
            <div className="flex items-center justify-center p-20">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-second"></div>
            </div>
        );
    }

    if (!scoreDetails) {
        return (
            <div className="min-h-screen bg-secondary-first px-7.5 pt-10">
                <p className="text-neutral-first">{t('score_definition_not_found')}</p>
            </div>
        );
    }

    return (
        <>
            <div className="pt-10 px-7.5 mb-6">
                <BreadcrumbBar breadcrumb={breadcrumb} />
            </div>

            <ConfigDetailsSummary
                title={scoreLabel}
                extraInfo1={registerDetails.register_mnemonic || t('none')}
                extraInfo2={
                    scoreDetails.is_enabled ? t('active') : t('inactive')
                }
                onView={() => setIsViewScoreModalOpen(true)}
                onEdit={
                    canEditScore
                        ? () => setIsEditScoreModalOpen(true)
                        : undefined
                }
            />

            <TopBar
                breadcrumb={[]}
                showFilters={false}
                showPagination
                showSubHeading
                subHeading={`${scoreLabel} — ${t('contributing_attributes')}`}
                showAddNewButton={canCreate}
                addNewButtonText={t('add_contributing_attribute')}
                onAddNewButton={() => setIsModalOpen(true)}
                pageStart={pagination.pageStart}
                pageEnd={pagination.pageEnd}
                total={pagination.total}
                onPrev={handlePrev}
                onNext={handleNext}
            />

            <ScoreContributingAttributesView
                isModalOpen={isModalOpen}
                onCloseModal={() => setIsModalOpen(false)}
                page={currentPage}
                pageSize={PAGE_SIZE}
                onDataLoaded={(totalItems, currentCount) =>
                    setPaginationInfo({ totalItems, currentCount })
                }
            />

            {isEditScoreModalOpen && (
                <EditScoreModal
                    key={scoreDetails.score_definition_id}
                    isOpen
                    onClose={() => setIsEditScoreModalOpen(false)}
                    onSuccess={refreshScores}
                    initialData={scoreDetails}
                />
            )}

            {isViewScoreModalOpen && (
                <ViewScoreDefinitionModal
                    onClose={() => setIsViewScoreModalOpen(false)}
                    data={scoreDetails}
                />
            )}
        </>
    );
};

export default ScoreDefinitionAttributesPage;
