'use client';

import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { useParams } from 'next/navigation';
import { useScoreContributingAttributes } from '../shared/hooks/useScoreContributingAttributes';
import { useFetch } from '@/shared/hooks';
import { toast } from 'react-toastify';
import { CONFIGURATION_TABS_ACTIONS } from '../shared/utils/configurationTabs.actions';
import Can from '@/components/shared/Can';
import { DataTable, DeleteButton, EditButton } from '../shared/components';
import AddScoreContributingAttributeModal from './AddScoreContributingAttributeModal';
import EditScoreContributingAttributeModal from './EditScoreContributingAttributeModal';
import type { ScoreContributingAttribute } from '../shared/types/registers';

interface ScoreContributingAttributesViewProps {
    isModalOpen: boolean;
    onCloseModal: () => void;
    page?: number;
    pageSize?: number;
    onDataLoaded?: (totalItems: number, currentCount: number) => void;
}

export default function ScoreContributingAttributesView({
    isModalOpen,
    onCloseModal,
    page = 1,
    pageSize = 10,
    onDataLoaded,
}: ScoreContributingAttributesViewProps) {
    const t = useTranslations();
    const { scoreDefinitionId } = useParams<{ scoreDefinitionId: string }>();

    const { contributingAttributes, loading, refresh, pagination } =
        useScoreContributingAttributes(scoreDefinitionId, page, pageSize);

    useEffect(() => {
        if (pagination && onDataLoaded) {
            onDataLoaded(pagination.number_of_items, contributingAttributes.length);
        }
    }, [pagination, contributingAttributes.length, onDataLoaded]);

    const { execute: deleteAttr } = useFetch();

    const [editModalOpen, setEditModalOpen] = useState(false);
    const [selected, setSelected] = useState<ScoreContributingAttribute | null>(null);

    const proceedDelete = async (id: string) => {
        const result = await deleteAttr(
            '/api/configuration/registers/score/attribute/delete-score-contributing-attributes',
            {
                method: 'POST',
                body: JSON.stringify({ contributing_attribute_id: id }),
            },
        );

        if (result && !(result as { error?: string }).error) {
            toast.success(t('toast_contributing_attribute_removed'));
            refresh();
        } else {
            toast.error(t('toast_contributing_attribute_remove_failed'));
        }
    };

    const handleDelete = (id: string) => {
        toast.info(
            ({ closeToast }) => (
                <div className="p-1">
                    <p className="font-bold text-neutral-first mb-3">
                        {t('confirm_remove_contributing_attribute')}
                    </p>
                    <div className="flex gap-3">
                        <button
                            type="button"
                            onClick={async () => {
                                closeToast();
                                await proceedDelete(id);
                            }}
                            className="bg-primary-second text-neutral-second px-4 py-1.5 rounded-full text-sm font-semibold hover:bg-primary-second transition-colors shadow-sm"
                        >
                            {t('remove')}
                        </button>
                        <button
                            type="button"
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

    const columns = [
        {
            key: 'attribute_name',
            label: t('attribute_name'),
        },

        {
            key: 'attribute_computation_required',
            label: t('attribute_computation_required'),
            render: (item: ScoreContributingAttribute) =>
                item.attribute_computation_required ? t('true') : t('false'),
        },
        {
            key: 'attribute_weightage',
            label: t('attribute_weightage_list_label'),
        },
    ];

    return (
        <>
            <DataTable
                columns={columns}
                data={contributingAttributes}
                loading={loading}
                rowKey={(item) => item.contributing_attribute_id}
                actions={(item) => (
                    <div className="flex gap-4">
                        <Can action={CONFIGURATION_TABS_ACTIONS.edit}>
                            <EditButton
                                label={t('edit')}
                                onClick={() => {
                                    setSelected(item);
                                    setEditModalOpen(true);
                                }}
                            />
                        </Can>
                        <Can action={CONFIGURATION_TABS_ACTIONS.delete}>
                            <DeleteButton
                                label={t('remove')}
                                onClick={() => handleDelete(item.contributing_attribute_id)}
                            />
                        </Can>
                    </div>
                )}
            />

            {isModalOpen && (
                <AddScoreContributingAttributeModal
                    isOpen
                    onClose={onCloseModal}
                    onSuccess={refresh}
                    scoreDefinitionId={scoreDefinitionId}
                />
            )}

            {editModalOpen && selected && (
                <EditScoreContributingAttributeModal
                    key={selected.contributing_attribute_id}
                    isOpen
                    onClose={() => {
                        setEditModalOpen(false);
                        setSelected(null);
                    }}
                    onSuccess={refresh}
                    initialData={selected}
                />
            )}
        </>
    );
}
