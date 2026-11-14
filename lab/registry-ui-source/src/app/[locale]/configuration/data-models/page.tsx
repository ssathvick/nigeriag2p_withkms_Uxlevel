'use client';

import { useState } from 'react';
import { TopBar } from '@/components/shared';
import { useFetch, usePagination } from '@/shared/hooks';
import { useRuntimeConfig } from '@/context/RuntimeConfigContext';
import { useRbac } from '@/context/RbacContext';
import { useTranslations } from 'next-intl';
import AddDataModelModal from '@/features/configuration/data-models/AddDataModelModal';
import EditDataModelModal from '@/features/configuration/data-models/EditDataModelModal';
import { useAllDataModels } from '@/features/configuration/shared/hooks/useAllDataModels';
import { CONFIGURATION_DATA_MODELS_ACTIONS } from '@/features/configuration/shared/utils/configurationDataModels.actions';
import Can from '@/components/shared/Can';
import { toast } from 'react-toastify';
import ConfirmRemovePopup from '@/features/configuration/shared/components/ConfirmRemovePopup';
import { DeleteButton, EditButton, DataTable, ViewButton } from '@/features/configuration/shared/components';
import ViewDataModelModal from '@/features/configuration/data-models/ViewDataModelModal';
import FileLink from '@/features/configuration/shared/components/FileLink';


type DataModel = {
    data_model_id: string;
    data_model_mnemonic: string;
    pattern_for_data_model: string;
    response_template_file_id: string;
    is_active: boolean;
};

const DataModelsConfigurationPage = () => {
    const t = useTranslations();
    const [modalType, setModalType] = useState<'add' | 'edit' | 'view' | null>(null);
    const [currentPage, setCurrentPage] = useState(1);
    const [showPopup, setShowPopup] = useState(false);
    const [selectedItem, setSelectedItem] = useState<DataModel | null>(null);

    const { execute: deleteDataModel } = useFetch();

    const proceedDelete = async (id: string, name: string) => {
        try {
            const result = await deleteDataModel('/api/configuration/data-models/delete', {
                method: 'POST',
                body: JSON.stringify({ data_model_id: id })
            });

            if (result) {
                toast.success(t('data_models_deleted_successfully'));
                refresh();
            } else {
                toast.error(t('data_model_deletion_failed'));
            }
        } catch (error) {
            console.error('Delete error');
        }
    };

    const handleDelete = (
        e: React.MouseEvent<HTMLButtonElement>,
        item: DataModel
    ) => {
        e.preventDefault();
        e.stopPropagation();

        setSelectedItem(item);
        setShowPopup(true);
    };

    const confirmDelete = async () => {
        if (!selectedItem) return;

        const { data_model_id, data_model_mnemonic } = selectedItem;

        await proceedDelete(data_model_id, data_model_mnemonic);

        setShowPopup(false);
        setSelectedItem(null);
    };

    const { config } = useRuntimeConfig();

    const { can } = useRbac();
    const canCreate = can(CONFIGURATION_DATA_MODELS_ACTIONS.create)

    const { dataModels, pagination, loading, refresh } = useAllDataModels(currentPage, config.pageSize || 100);

    const { pageStart, pageEnd, total } = usePagination({
        totalItems: pagination?.number_of_items || 0,
        currentPage: currentPage,
        pageSize: config.pageSize || 10,
        currentCount: dataModels.length,
    });


    const handlePrev = () => {
        setCurrentPage((prev) => Math.max(1, prev - 1));
    };

    const handleNext = () => {
        setCurrentPage((prev) => prev + 1);
    };

    const columns = [
        {
            key: 'data_model_mnemonic',
            label: t('data_model_mnemonic'),
        },
        {
            key: 'response_template_file_id',
            label: t('template_id'),
            render: (item: DataModel) => (
                <FileLink
                    documentId={item.response_template_file_id}
                />
            ),
        },
        {
            key: 'is_active',
            label: t('status'),
            render: (item: DataModel) =>
                item.is_active ? (
                    <span className="text-toast-success">{t('active')}</span>
                ) : (
                    <span className="text-toast-failed">{t('inactive')}</span>
                ),
        },
    ];

    return (
        <>
            <TopBar
                breadcrumb={[{ label: t('data_models') }]}
                showFilters={false}
                showPagination
                showAddNewButton={canCreate}
                addNewButtonText={t('add_new_data_model')}
                onAddNewButton={() => setModalType('add')}
                pageStart={pageStart}
                pageEnd={pageEnd}
                total={total}
                onPrev={handlePrev}
                onNext={handleNext}
            />

            <DataTable
                columns={columns}
                data={dataModels}
                loading={loading}
                rowKey={(item) => item.data_model_id}
                actions={(item) => (
                    <>
                        <ViewButton
                            label={t('view')}
                            onClick={() => {
                                setSelectedItem(item);
                                setModalType('view');
                            }}
                        />
                        <Can action={CONFIGURATION_DATA_MODELS_ACTIONS.edit}>
                            <EditButton
                                label={t('common.edit')}
                                onClick={() => {
                                    setSelectedItem(item);
                                    setModalType('edit');
                                }}
                            />
                        </Can>

                        <Can action={CONFIGURATION_DATA_MODELS_ACTIONS.delete}>
                            <DeleteButton
                                label={t('remove')}
                                onClick={(e) => handleDelete(e, item)}
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
                    onConfirm={confirmDelete}
                    messageKey='confirm_remove_data_model'
                />
            )}

            {modalType === 'view' && (
                <ViewDataModelModal
                    data={selectedItem}
                    onClose={() => {
                        setModalType(null);
                        setSelectedItem(null);
                    }}
                />)}

            {modalType === 'add' && (
                <AddDataModelModal
                    onClose={() => setModalType(null)}
                    onSuccess={() => {
                        refresh();
                    }}
                />
            )}

            {modalType === 'edit' && (
                <EditDataModelModal
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

export default DataModelsConfigurationPage;
