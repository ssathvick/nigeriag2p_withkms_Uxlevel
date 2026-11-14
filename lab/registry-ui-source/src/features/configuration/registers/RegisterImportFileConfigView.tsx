'use client';

import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { useParams } from 'next/navigation';
import { useFetch } from '@/shared/hooks';
import { toast } from 'react-toastify';
import Can from '@/components/shared/Can';
import { CONFIGURATION_TABS_ACTIONS } from '../shared/utils/configurationTabs.actions';
import { DataTable, DeleteButton, EditButton } from '../shared/components';
import {
    ImportFileConfiguration,
    useAllImportFileConfigurations,
} from '@/features/configuration/shared/hooks/useAllImportFileConfigurations';
import AddImportFileConfigModal from './AddImportFileConfigModal';
import EditImportFileConfigModal from './EditImportFileConfigModal';

interface RegisterImportFileConfigViewProps {
    isModalOpen: boolean;
    onCloseModal: () => void;
    currentPage?: number;
    pageSize?: number;
    onDataLoaded?: (totalItems: number, currentCount: number) => void;
}

export default function RegisterImportFileConfigView({
    isModalOpen,
    onCloseModal,
    currentPage = 1,
    pageSize = 10,
    onDataLoaded,
}: RegisterImportFileConfigViewProps) {
    const t = useTranslations();
    const { registerId } = useParams<{ registerId: string }>();
    const { importFileConfigurations, loading, pagination, refresh } = useAllImportFileConfigurations(
        registerId,
        currentPage,
        pageSize,
    );
    const { execute: deleteConfig } = useFetch();

    const [editModalOpen, setEditModalOpen] = useState(false);
    const [selectedConfig, setSelectedConfig] = useState<ImportFileConfiguration | null>(null);

    useEffect(() => {
        if (pagination && onDataLoaded) {
            onDataLoaded(pagination.number_of_items, importFileConfigurations.length);
        }
    }, [pagination, importFileConfigurations.length, onDataLoaded]);

    const proceedDelete = async (config: ImportFileConfiguration) => {
        const result = await deleteConfig(
            '/api/input-mechanism/delete-import-file-configuration',
            {
                method: 'POST',
                body: JSON.stringify({
                    import_file_configuration_id: config.import_file_configuration_id,
                    register_id: config.register_id,
                    form_id: config.form_id,
                    data_model_id: config.data_model_id,
                    import_file_template_mnemonic: config.import_file_template_mnemonic,
                    import_file_template_description: config.import_file_template_description ?? '',
                }),
            },
        );

        if (result?.import_file_configuration_id) {
            toast.success(t('toast_import_file_config_removed'));
            refresh();
        } else {
            toast.error(t('toast_import_file_config_remove_failed'));
        }
    };

    const handleDelete = (config: ImportFileConfiguration) => {
        toast.info(
            ({ closeToast }) => (
                <div className="p-1">
                    <p className="font-bold text-neutral-first mb-3">
                        {t('confirm_remove_import_file_config')}
                    </p>
                    <div className="flex gap-3">
                        <button
                            onClick={async () => {
                                closeToast();
                                await proceedDelete(config);
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
            key: 'import_file_template_mnemonic',
            label: t('template_mnemonic'),
        },
        {
            key: 'import_file_template_description',
            label: t('template_description'),
        },
        {
            key: 'form_id',
            label: t('form_id'),
        },
    ];

    return (
        <>
            <DataTable
                columns={columns}
                data={importFileConfigurations}
                loading={loading}
                rowKey={(item: ImportFileConfiguration) => item.import_file_configuration_id}
                actions={(item) => (
                    <div className="flex gap-4">

                        <Can action={CONFIGURATION_TABS_ACTIONS.edit}>
                            <EditButton
                                label={t('common.edit')}
                                onClick={() => {
                                    setSelectedConfig(item);
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

            <AddImportFileConfigModal
                isOpen={isModalOpen}
                onClose={onCloseModal}
                onSuccess={refresh}
            />


            <EditImportFileConfigModal
                isOpen={editModalOpen}
                onClose={() => {
                    setEditModalOpen(false);
                    setSelectedConfig(null);
                }}
                onSuccess={refresh}
                initialData={selectedConfig}
            />
        </>
    );
}
