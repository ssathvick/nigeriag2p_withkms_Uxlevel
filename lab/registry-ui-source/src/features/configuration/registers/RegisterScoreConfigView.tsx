'use client';

import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { useParams } from 'next/navigation';
import { useRouter } from '@/i18n/navigation';
import { useScoreDefinitions } from '../shared/hooks/useScoreDefinitions';
import { useFetch } from '@/shared/hooks';
import { toast } from 'react-toastify';
import { CONFIGURATION_TABS_ACTIONS } from '../shared/utils/configurationTabs.actions';
import Can from '@/components/shared/Can';
import { DataTable, DeleteButton, EditButton } from '../shared/components';
import AddScoreModal from './AddScoreModal';
import EditScoreModal from './EditScoreModal';
import type { ScoreDefinition } from '../shared/types/registers';

interface RegisterScoreConfigViewProps {
    isModalOpen: boolean;
    onCloseModal: () => void;
    currentPage?: number;
    pageSize?: number;
    onDataLoaded?: (totalItems: number, currentCount: number) => void;
}

export default function RegisterScoreConfigView({
    isModalOpen,
    onCloseModal,
    currentPage = 1,
    pageSize = 10,
    onDataLoaded,
}: RegisterScoreConfigViewProps) {
    const t = useTranslations();
    const router = useRouter();
    const { registerId } = useParams<{ registerId: string }>();
    const { scoreDefinitions, loading, refresh, pagination } = useScoreDefinitions(
        registerId,
        currentPage,
        pageSize,
    );

    useEffect(() => {
        if (pagination && onDataLoaded) {
            onDataLoaded(pagination.number_of_items, scoreDefinitions.length);
        }
    }, [pagination, scoreDefinitions.length, onDataLoaded]);

    const { execute: deleteScore } = useFetch();

    const [editModalOpen, setEditModalOpen] = useState(false);
    const [selectedScore, setSelectedScore] = useState<ScoreDefinition | null>(null);

    const proceedDelete = async (scoreDefinitionId: string) => {
        const result = await deleteScore('/api/configuration/registers/score/delete-score-definitions', {
            method: 'POST',
            body: JSON.stringify({ score_definition_id: scoreDefinitionId }),
        });

        if (result && !(result as { error?: string }).error) {
            toast.success(t('toast_score_removed'));
            refresh();
        } else {
            toast.error(t('toast_score_remove_failed'));
        }
    };

    const handleDelete = (scoreDefinitionId: string) => {
        toast.info(
            ({ closeToast }) => (
                <div className="p-1">
                    <p className="font-bold text-neutral-first mb-3">{t('confirm_remove_score')}</p>
                    <div className="flex gap-3">
                        <button
                            onClick={async () => {
                                closeToast();
                                await proceedDelete(scoreDefinitionId);
                            }}
                            className="bg-primary-second text-neutral-second px-4 py-1.5 rounded-full text-sm font-semibold hover:bg-primary-second transition-colors shadow-sm"
                        >
                            {t('remove')}
                        </button>
                        <button
                            onClick={closeToast}
                            className="bg-secondary-first text-neutral-first/70 px-4 py-1.5 rounded-full text-sm font-semibold hover:bg-secondary-second transition-colors"
                        >
                            {t('cancel')}
                        </button>
                    </div>
                </div>
            ),
            {
                position: 'top-right',
                autoClose: false,
                closeOnClick: false,
                draggable: false,
                closeButton: false,
                className: 'rounded-[15px] shadow-xl border border-secondary-first',
            },
        );
    };

    const handleEdit = (item: ScoreDefinition) => {
        setSelectedScore(item);
        setEditModalOpen(true);
    };

    const columns = [
        {
            key: 'score_type',
            label: t('score_type'),
        },
        {
            key: 'is_enabled',
            label: t('status'),
            render: (item: ScoreDefinition) => (item.is_enabled ? t('active') : t('inactive')),
        },
    ];

    return (
        <>
            <DataTable
                columns={columns}
                data={scoreDefinitions}
                loading={loading}
                rowKey={(item) => item.score_definition_id}
                onRowClick={(item) =>
                    router.push(
                        `/configuration/registers/${registerId}/scores/${item.score_definition_id}`,
                    )
                }
                actions={(item) => (
                    <div className="flex gap-4">
                        <Can action={CONFIGURATION_TABS_ACTIONS.edit}>
                            <EditButton label={t('edit')} onClick={() => handleEdit(item)} />
                        </Can>
                        <Can action={CONFIGURATION_TABS_ACTIONS.delete}>
                            <DeleteButton label={t('remove')} onClick={() => handleDelete(item.score_definition_id)} />
                        </Can>
                    </div>
                )}
            />

            {isModalOpen && (
                <AddScoreModal isOpen onClose={onCloseModal} onSuccess={refresh} />
            )}

            {editModalOpen && selectedScore && (
                <EditScoreModal
                    key={selectedScore.score_definition_id}
                    isOpen
                    onClose={() => {
                        setEditModalOpen(false);
                        setSelectedScore(null);
                    }}
                    onSuccess={refresh}
                    initialData={selectedScore}
                />
            )}
        </>
    );
}
