'use client';

import { useState } from 'react';
import { TopBar } from '@/components/shared';
import { useAllIncomingKeyPaths, useIncomingKeyPath } from '@/features/configuration/shared';
import { usePagination, useFetch } from '@/shared/hooks';
import { useRuntimeConfig } from '@/context/RuntimeConfigContext';
import { useTranslations } from 'next-intl';
import { IncomingKeyPath } from '@/features/configuration/shared/hooks/useAllIncomingKeyPaths';
import { toast } from 'react-toastify';
import { useRbac } from '@/context/RbacContext';
import { CONFIGURATION_KEY_PATHS_ACTIONS } from '@/features/configuration/shared/utils/configurationKeyPaths.actions';
import Can from '@/components/shared/Can';
import { DeleteButton, EditButton, ViewButton, DataTable } from '@/features/configuration/shared/components';
import { AddKeyPathModal, EditKeyPathModal, ViewKeyPathModal } from '@/features/configuration/ingest';
import ConfirmRemovePopup from '@/features/configuration/shared/components/ConfirmRemovePopup';


const KeyPathsPage = () => {
    const t = useTranslations();
    const [modalType, setModalType] = useState<'add' | 'edit' | 'view' | null>(null);
    const [currentPage, setCurrentPage] = useState(1);
    const [showPopup, setShowPopup] = useState(false);
    const [selectedItem, setSelectedItem] = useState<IncomingKeyPath | null>(null);

    const { config } = useRuntimeConfig();
    const { can } = useRbac();
    const { execute: deleteKeyPath } = useFetch();
    const { selectedKeyPath, fetchKeyPath } = useIncomingKeyPath();
    const { keyPaths, pagination, loading, refresh } = useAllIncomingKeyPaths(currentPage, config.pageSize);

    const { pageStart, pageEnd, total } = usePagination({
        totalItems: pagination?.number_of_items || 0,
        currentPage: currentPage,
        pageSize: config.pageSize || 10,
        currentCount: keyPaths.length,
    });

    const handlePrev = () => {
        setCurrentPage((prev) => Math.max(1, prev - 1));
    };

    const handleNext = () => {
        setCurrentPage((prev) => prev + 1);
    };

    const handleView = async (keyPath: IncomingKeyPath) => {
        const result = await fetchKeyPath(keyPath.key_path_id);
        if (result) {
            setModalType('view');
        }
    };

    const handleUpdate = async (keyPath: IncomingKeyPath) => {
        const result = await fetchKeyPath(keyPath.key_path_id);
        if (result) {
            setModalType('edit');
        }
    };

    const proceedDelete = async (id: string) => {
        try {
            const result = await deleteKeyPath('/api/configuration/ingest/delete-key-path', {
                method: 'POST',
                body: JSON.stringify({ key_path_id: id })
            });

            if (result?.key_path_id) {
                toast.success(t('toast_key_path_removed'));
                refresh();
            } else {
                toast.error(t('toast_key_path_remove_failed'));
            }
        } catch (error) {
            toast.error(t('toast_operation_failed'));
        }
    };

    const handleConfirmDelete = async () => {
        if (!selectedItem) return;

        await proceedDelete(selectedItem.key_path_id);

        setShowPopup(false);
        setSelectedItem(null);
    };

    const handleDelete = (keyPath: IncomingKeyPath) => {
        setSelectedItem(keyPath);
        setShowPopup(true);
    };

    const columns = [
        // {
        //     key: 'key_path_id',
        //     label: t('key_path_id'),
        // },
        {
            key: 'data_model',
            label: t('data_model_mnemonic'),
            render: (item: IncomingKeyPath) =>
                item.data_model_mnemonic || item.data_model_id,
        },
        {
            key: 'is_list',
            label: t('is_list'),
            render: (item: IncomingKeyPath) =>
                item.is_list ? t('true') : t('false'),
        },
    ];

    return (
        <>
            <TopBar
                breadcrumb={[{ label: t('ingest_configurations') }, { label: t('ingest_key_paths') }]}
                showFilters={false}
                showPagination
                showAddNewButton={can(CONFIGURATION_KEY_PATHS_ACTIONS.create)}
                addNewButtonText={t('add_new_key_path')}
                onAddNewButton={() => setModalType('add')}
                pageStart={pageStart}
                pageEnd={pageEnd}
                total={total}
                onPrev={handlePrev}
                onNext={handleNext}
            />

            <DataTable
                columns={columns}
                data={keyPaths}
                loading={loading}
                rowKey={(item) => item.key_path_id}
                actions={(item) => (
                    <>
                        <ViewButton
                            label={t('view')}
                            onClick={() => handleView(item)}
                        />

                        <Can action={CONFIGURATION_KEY_PATHS_ACTIONS.edit}>
                            <EditButton
                                label={t('common.edit')}
                                onClick={() => handleUpdate(item)}
                            />
                        </Can>

                        <Can action={CONFIGURATION_KEY_PATHS_ACTIONS.delete}>
                            <DeleteButton
                                label={t('remove')}
                                onClick={() => handleDelete(item)}
                            />
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
                    onConfirm={handleConfirmDelete}
                    messageKey='confirm_remove_ingest_key_path'
                />
            )}

            {modalType === 'add' && (
                <AddKeyPathModal
                    onClose={() => setModalType(null)}
                    onSuccess={refresh}
                />
            )}

            {modalType === 'view' && (
                <ViewKeyPathModal
                    onClose={() => setModalType(null)}
                    data={selectedKeyPath}
                />
            )}
            {modalType === 'edit' && (
                <EditKeyPathModal
                    onClose={() => setModalType(null)}
                    initialData={selectedKeyPath}
                    onSuccess={refresh}
                />
            )}
        </>
    );
};

export default KeyPathsPage;
