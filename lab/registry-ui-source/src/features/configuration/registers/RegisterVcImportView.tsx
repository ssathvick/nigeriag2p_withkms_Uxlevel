'use client';

import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { useParams } from 'next/navigation';
import { useFetch } from '@/shared/hooks';
import { toast } from 'react-toastify';
import Can from '@/components/shared/Can';
import { CONFIGURATION_TABS_ACTIONS } from '../shared/utils/configurationTabs.actions';
import { DataTable, DeleteButton, EditButton } from '../shared/components';
import { VcImport, useAllVcImports } from '@/features/configuration/shared/hooks/useAllVcImports';
import AddVcImportModal from './AddVcImportModal';
import EditVcImportModal from './EditVcImportModal';

interface RegisterVcImportViewProps {
    isModalOpen: boolean;
    onCloseModal: () => void;
    currentPage?: number;
    pageSize?: number;
    onDataLoaded?: (totalItems: number, currentCount: number) => void;
}

export default function RegisterVcImportView({
    isModalOpen,
    onCloseModal,
    currentPage = 1,
    pageSize = 10,
    onDataLoaded,
}: RegisterVcImportViewProps) {
    const t = useTranslations();
    const { registerId } = useParams<{ registerId: string }>();
    const { vcImports, loading, pagination, refresh } = useAllVcImports(
        registerId,
        currentPage,
        pageSize,
    );
    const { execute: deleteConfig } = useFetch();

    const [editModalOpen, setEditModalOpen] = useState(false);
    const [selectedVcImport, setSelectedVcImport] = useState<VcImport | null>(null);

    useEffect(() => {
        if (pagination && onDataLoaded) {
            onDataLoaded(pagination.number_of_items, vcImports.length);
        }
    }, [pagination, vcImports.length, onDataLoaded]);

    const proceedDelete = async (vcImport: VcImport) => {
        const result = await deleteConfig('/api/input-mechanism/delete-vc-configuration', {
            method: 'POST',
            body: JSON.stringify({
                vc_config_id: vcImport.vc_config_id,
                register_id: vcImport.register_id,
                intake_form_id: vcImport.intake_form_id,
                data_model_id: vcImport.data_model_id,
                vc_mnemonic: vcImport.vc_mnemonic,
                descriptor_schema: vcImport.descriptor_schema ?? {},
            }),
        });

        if (result?.vc_config_id) {
            toast.success(t('toast_vc_import_removed'));
            refresh();
        } else {
            toast.error(t('toast_vc_import_remove_failed'));
        }
    };

    const handleDelete = (vcImport: VcImport) => {
        toast.info(
            ({ closeToast }) => (
                <div className="p-1">
                    <p className="font-bold text-neutral-first mb-3">
                        {t('confirm_remove_vc_import')}
                    </p>
                    <div className="flex gap-3">
                        <button
                            onClick={async () => {
                                closeToast();
                                await proceedDelete(vcImport);
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

    const columns = [
        {
            key: 'vc_mnemonic',
            label: t('vc_mnemonic'),
        },
        {
            key: 'intake_form_id',
            label: t('form_id'),
        },
        {
            key: 'data_model_id',
            label: t('data_model_id'),
        },
    ];

    return (
        <>
            <DataTable
                columns={columns}
                data={vcImports}
                loading={loading}
                rowKey={(item: VcImport) => item.vc_config_id}
                actions={(item) => (
                    <div className="flex gap-4">
                        <Can action={CONFIGURATION_TABS_ACTIONS.edit}>
                            <EditButton
                                label={t('common.edit')}
                                onClick={() => {
                                    setSelectedVcImport(item);
                                    setEditModalOpen(true);
                                }}
                            />
                        </Can>
                        <Can action={CONFIGURATION_TABS_ACTIONS.delete}>
                            <DeleteButton
                                label={t('remove')}
                                onClick={() => handleDelete(item)}
                            />
                        </Can>
                    </div>
                )}
            />

            <AddVcImportModal
                isOpen={isModalOpen}
                onClose={onCloseModal}
                onSuccess={refresh}
            />

            <EditVcImportModal
                isOpen={editModalOpen}
                onClose={() => {
                    setEditModalOpen(false);
                    setSelectedVcImport(null);
                }}
                onSuccess={refresh}
                initialData={selectedVcImport}
            />
        </>
    );
}
