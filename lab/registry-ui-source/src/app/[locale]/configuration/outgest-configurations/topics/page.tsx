'use client';

import { useState } from 'react';
import { TopBar } from '@/components/shared';
import { useFetch, usePagination } from '@/shared/hooks';
import { useRuntimeConfig } from '@/context/RuntimeConfigContext';
import { useRbac } from '@/context/RbacContext';
import { useTranslations } from 'next-intl';
import Can from '@/components/shared/Can';
import { toast } from 'react-toastify';
import { CONFIGURATION_OUTGESTION_TOPICS_ACTIONS } from '@/features/configuration/shared/utils/configurationOutgestionTopics.actions';
import AddOutgestionTopicModal from '@/features/configuration/outgest/AddOutgestionTopicModal';
import EditOutgestionTopicModal from '@/features/configuration/outgest/EditOutgestionTopicModal';
import ConfirmRemovePopup from '@/features/configuration/shared/components/ConfirmRemovePopup';
import ViewOutgestionTopicModal from '@/features/configuration/outgest/ViewOutgestionTopicModal';
import { useAllOutgestTopics } from '@/features/configuration/shared/hooks/useAllOutgestTopics';
import { DeleteButton, EditButton, ViewButton, DataTable } from '@/features/configuration/shared/components';
import ToggleStatusSwitch from '@/features/configuration/shared/components/ToggleStatusSwitch';


export interface OutgestTopic {
    topic_id: string;
    register_id: string;
    register_mnemonic: string;
    data_model_id: string;
    data_model_mnemonic: string;
    websub_topic: string;
    description: string;
    is_active: boolean;
    websub_register_status: string;
    websub_register_datetime: string;
    websub_register_number_of_attempts: string;
    websub_register_latest_error_message: string;
}


const OutgestTopicsPage = () => {
    const t = useTranslations();

    const [currentPage, setCurrentPage] = useState(1);
    const [modalType, setModalType] = useState<'add' | 'edit' | 'view' | null>(null);
    const [selectedItem, setSelectedItem] = useState<OutgestTopic | null>(null);
    const [showPopup, setShowPopup] = useState(false);

    const { execute: deleteOutgestionTopic } = useFetch();
    const { execute: toggleTopicStatus } = useFetch();

    const proceedDelete = async (id: string) => {
        try {
            const result = await deleteOutgestionTopic('/api/configuration/outgest/delete-topic', {
                method: 'POST',
                body: JSON.stringify({ topic_id: id })
            });

            if (result) {
                toast.success(t("topic_deleted_success"));
                refresh();
            } else {
                toast.error(t('topic_deletion_failed'));
            }
        } catch (error) {
            toast.error(t('topic_deletion_failed'));
        }
    };

    const handleToggleStatus = async (
        e: React.MouseEvent<HTMLButtonElement>,
        item: OutgestTopic
    ) => {
        e.preventDefault();
        e.stopPropagation();

        try {
            const result = await toggleTopicStatus(
                '/api/configuration/outgest/toggle-topic-status',
                {
                    method: 'POST',
                    body: JSON.stringify({
                        topic_id: item.topic_id,
                    }),
                }
            );

            if (result) {
                toast.success(t('topic_toggle_success'));
                refresh();
            } else {
                toast.error(t('topic_toggle_failed'));
            }
        } catch (error) {
            toast.error(t('topic_toggle_failed'));
        }
    };

    const handleDelete = (
        e: React.MouseEvent<HTMLButtonElement>,
        item: OutgestTopic
    ) => {
        e.preventDefault();
        e.stopPropagation();

        setSelectedItem(item);
        setShowPopup(true);
    };

    const confirmDelete = async () => {
        if (!selectedItem) return;

        const { topic_id } = selectedItem;

        await proceedDelete(topic_id);

        setShowPopup(false);
        setSelectedItem(null);
    };

    const { config } = useRuntimeConfig();

    const { can } = useRbac();
    const canCreate = can(CONFIGURATION_OUTGESTION_TOPICS_ACTIONS.create)
    const canEdit = can(CONFIGURATION_OUTGESTION_TOPICS_ACTIONS.edit);

    const { topics, pagination, loading, refresh } = useAllOutgestTopics(currentPage, config.pageSize);


    const { pageStart, pageEnd, total } = usePagination({
        totalItems: pagination?.number_of_items || 0,
        currentPage: currentPage,
        pageSize: config.pageSize || 10,
        currentCount: topics.length,
    });


    const handlePrev = () => {
        setCurrentPage((prev) => Math.max(1, prev - 1));
    };

    const handleNext = () => {
        setCurrentPage((prev) => prev + 1);
    };

    const topicColumns = [
        {
            key: 'data_model_mnemonic',
            label: t('data_model_mnemonic')
        },
        {
            key: 'register_mnemonic',
            label: t('register_mnemonic')
        },
        {
            key: 'websub_topic',
            label: t('websub_topic')
        },
        {
            key: 'is_active',
            label: t('status'),
            render: (item: OutgestTopic) => (
                <ToggleStatusSwitch
                    disabled={!canEdit}
                    isActive={item.is_active}
                    onToggle={(e) => handleToggleStatus(e, item)}
                />
            ),
        }
    ];

    return (
        <>
            <TopBar
                breadcrumb={[{ label: t('outgest_configurations') }, { label: t('outgest_topics') }]}
                showFilters={false}
                showPagination
                showAddNewButton={canCreate}
                addNewButtonText={t('add_new_outgestion_topic')}
                onAddNewButton={() => setModalType('add')}
                pageStart={pageStart}
                pageEnd={pageEnd}
                total={total}
                onPrev={handlePrev}
                onNext={handleNext}
            />

            <DataTable
                columns={topicColumns}
                data={topics}
                loading={loading}
                rowKey={(i) => i.topic_id}
                actions={(item) => (
                    <>
                        <ViewButton
                            label={t('view')}
                            onClick={() => {
                                setSelectedItem(item);
                                setModalType('view');
                            }}
                        />

                        <Can action={CONFIGURATION_OUTGESTION_TOPICS_ACTIONS.edit}>
                            <EditButton
                                label={t('common.edit')}
                                onClick={() => {
                                    setSelectedItem(item);
                                    setModalType('edit');
                                }}
                            />
                        </Can>

                        <Can action={CONFIGURATION_OUTGESTION_TOPICS_ACTIONS.delete}>
                            {!item.is_active && (
                                <DeleteButton
                                    label={t('remove')}
                                    onClick={(e) => handleDelete(e, item)}
                                />
                            )}
                        </Can>
                    </>
                )}
            />

            {showPopup && (
                <ConfirmRemovePopup
                    onClose={() => {
                        setShowPopup(false);
                        setSelectedItem(null);
                    }}
                    onConfirm={confirmDelete}
                    messageKey='confirm_remove_outgestion_topic'
                />
            )}

            {modalType === 'view' && (
                <ViewOutgestionTopicModal
                    data={selectedItem}
                    onClose={() => {
                        setModalType(null);
                        setSelectedItem(null);
                    }}
                />
            )}

            {modalType === 'add' && (
                <AddOutgestionTopicModal
                    onClose={() => setModalType(null)}
                    onSuccess={() => {
                        refresh();
                    }}
                />
            )}

            {modalType === 'edit' && (
                <EditOutgestionTopicModal
                    data={selectedItem}
                    onClose={() => {
                        setModalType(null);
                        setSelectedItem(null);
                    }}
                    onSuccess={() => {
                        refresh();
                    }}
                />
            )}
        </>
    );
};

export default OutgestTopicsPage;
