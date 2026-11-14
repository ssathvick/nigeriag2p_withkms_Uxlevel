'use client';

import { useState } from 'react';
import { TopBar } from '@/components/shared';
import { useFetch, usePagination } from '@/shared/hooks';
import { useRuntimeConfig } from '@/context/RuntimeConfigContext';
import { useRbac } from '@/context/RbacContext';
import { useTranslations } from 'next-intl';
import Can from '@/components/shared/Can';
import { toast } from 'react-toastify';
import { useAllOutgestTemplates } from '@/features/configuration/shared/hooks/useAllOutgestTemplates';
import { CONFIGURATION_OUTGESTION_TEMPLATES_ACTIONS } from '@/features/configuration/shared/utils/configurationOutgestionTemplates.actions';
import ConfirmRemovePopup from '@/features/configuration/shared/components/ConfirmRemovePopup';
import { AddOutgestionTemplateModal, EditOutgestionTemplateModal, ViewOutgestionTemplateModal } from '@/features/configuration/outgest';
import { DeleteButton, EditButton, ViewButton, DataTable, FileLink } from '@/features/configuration/shared/components';


type OutgestTemplate = {
    template_id: string;
    register_id: string;
    data_model_id: string;
    template_file_id: string;
}


const OutgestTemplatesPage = () => {
    const t = useTranslations();
    const [modalType, setModalType] = useState<'add' | 'edit' | 'view' | null>(null);
    const [selectedItem, setSelectedItem] = useState<OutgestTemplate | null>(null);
    const [currentPage, setCurrentPage] = useState(1);


    const [showPopup, setShowPopup] = useState(false);

    const { execute: deleteOutgestionTemplate } = useFetch();

    const proceedDelete = async (id: string) => {
        try {
            const result = await deleteOutgestionTemplate('/api/configuration/outgest/delete-template', {
                method: 'POST',
                body: JSON.stringify({ template_id: id })
            });

            if (result) {
                toast.success(t("outgest_template_deleted_success"));
                refresh();
            } else {
               toast.error(t('outgest_template_deletion_failed'));
            }
        } catch (error) {
            console.error('Delete error');
        }
    };

    const handleDelete = (
        e: React.MouseEvent<HTMLButtonElement>,
        item: OutgestTemplate
    ) => {
        e.preventDefault();
        e.stopPropagation();

        setSelectedItem(item);
        setShowPopup(true);
    };

    const confirmDelete = async () => {
        if (!selectedItem) return;

        const { template_id } = selectedItem;

        await proceedDelete(template_id);

        setShowPopup(false);
        setSelectedItem(null);
    };

    const { config } = useRuntimeConfig();

    const { can } = useRbac();
    const canCreate = can(CONFIGURATION_OUTGESTION_TEMPLATES_ACTIONS.create)

    const { templates, pagination, loading, refresh } = useAllOutgestTemplates(currentPage, config.pageSize);


    const { pageStart, pageEnd, total } = usePagination({
        totalItems: pagination?.number_of_items || 0,
        currentPage: currentPage,
        pageSize: config.pageSize || 10,
        currentCount: templates.length,
    });


    const handlePrev = () => {
        setCurrentPage((prev) => Math.max(1, prev - 1));
    };

    const handleNext = () => {
        setCurrentPage((prev) => prev + 1);
    };

    const templateColumns = [
        {
            key: 'data_model_mnemonic',
            label: t('data_model_mnemonic')
        },
        {
            key: 'register_mnemonic',
            label: t('register_mnemonic')
        },
        {
            key: 'template_file_id',
            label: t('template_file_id'),
            render: (item: OutgestTemplate) => (
                <FileLink
                    documentId={item.template_file_id}
                />
            ),
        },
    ];

    return (
        <>
            <TopBar
                breadcrumb={[{ label: t('outgest_configurations') }, { label: t('outgest_templates') }]}
                showFilters={false}
                showPagination
                showAddNewButton={canCreate}
                addNewButtonText={t('add_new_outgestion_template')}
                onAddNewButton={() => setModalType('add')}
                pageStart={pageStart}
                pageEnd={pageEnd}
                total={total}
                onPrev={handlePrev}
                onNext={handleNext}
            />

            <DataTable
                columns={templateColumns}
                data={templates}
                loading={loading}
                rowKey={(i) => i.template_id}
                actions={(item) => (
                    <>
                        <ViewButton
                            label={t('view')}
                            onClick={() => {
                                setSelectedItem(item);
                                setModalType('view');
                            }}
                        />

                        <Can action={CONFIGURATION_OUTGESTION_TEMPLATES_ACTIONS.edit}>
                            <EditButton
                                label={t('common.edit')}
                                onClick={() => {
                                    setSelectedItem(item);
                                    setModalType('edit');
                                }}
                            />
                        </Can>

                        <Can action={CONFIGURATION_OUTGESTION_TEMPLATES_ACTIONS.delete}>
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
                    messageKey='confirm_remove_outgestion_template'
                />
            )}

            {modalType === 'view' && (
                <ViewOutgestionTemplateModal
                    data={selectedItem}
                    onClose={() => {
                        setModalType(null);
                        setSelectedItem(null);
                    }}
                />)}

            {modalType === 'add' && (
                <AddOutgestionTemplateModal
                    onClose={() => setModalType(null)}
                    onSuccess={refresh}
                />
            )}

            {modalType === 'edit' && (
                <EditOutgestionTemplateModal
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

export default OutgestTemplatesPage;
