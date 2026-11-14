'use client';

import { useState } from 'react';
import { useRouter } from '@/i18n/navigation';
import { useTranslations } from 'next-intl';
import AddRegisterModal from './AddRegisterModal';
import ViewRegisterFieldsModal from './ViewRegisterFieldsModal';
import { Register } from '../shared/types';

import Image from 'next/image';

import { useFetch } from '@/shared/hooks';

import { toast } from 'react-toastify';
import { CONFIGURATION_REGISTERS_ACTIONS } from '../shared/utils/configurationRegisters.actions';
import Can from '@/components/shared/Can';
import { DataTable, DeleteButton, ViewButton } from '../shared/components';
import ConfirmRemovePopup from '../shared/components/ConfirmRemovePopup';

interface RegistersConfigViewProps {
    registers: Register[];
    loading: boolean;
    refresh: () => void;
    onAddNewRegister: () => void;
    isModalOpen: boolean;
    onCloseModal: () => void;
    registerId?: string;
}

export default function RegistersConfigView({
    registers,
    loading,
    refresh,
    isModalOpen,
    onCloseModal,
}: RegistersConfigViewProps) {
    const t = useTranslations();
    const router = useRouter();
    const { execute: deleteRegister } = useFetch();
    const [isViewModalOpen, setIsViewModalOpen] = useState(false);
    const [viewData, setViewData] = useState<Register | undefined>(undefined);
    const [showDeletePopup, setShowDeletePopup] = useState(false);
    const [selectedRegister, setSelectedRegister] = useState<Register | null>(null);

    const proceedDelete = async (id: string, name: string) => {
        try {
            const result = await deleteRegister('/api/configuration/registers/delete', {
                method: 'POST',
                body: JSON.stringify({ register_id: id })
            });

            if (result) {
                toast.success(t('toast_register_deleted', { name }));
                refresh();
            } else {
                toast.error(t('toast_register_delete_failed'));
            }
        } catch (error) {
            toast.error(t('toast_register_delete_error'));
        }
    };

    const handleDelete = async (register: Register) => {
        if (register.has_data) {
            toast.error(t('toast_register_delete_has_data'));
            return;
        }
        setSelectedRegister(register);
        setShowDeletePopup(true);
    };

    const handleConfirmDelete = async () => {
        if (!selectedRegister) return;
        await proceedDelete(selectedRegister.register_id, selectedRegister.register_mnemonic);
        setShowDeletePopup(false);
        setSelectedRegister(null);
    };

    const handleView = (register: Register) => {
        setViewData(register);
        setIsViewModalOpen(true);
    };

    const columns = [
        {
            key: 'icon',
            label: t('icon'),
            render: (item: Register) =>
                item.register_icon ? (
                    <Image
                        src={
                            item.register_icon.startsWith('data:')
                                ? item.register_icon
                                : `data:image/png;base64,${item.register_icon}`
                        }
                        alt={item.register_mnemonic}
                        width={40}
                        height={40}
                        className="rounded-[10px] object-contain"
                    />
                ) : (
                    <div className="w-8 h-8 bg-secondary-third border border-gray-200 rounded-[10px]" />
                ),
        },
        {
            key: 'register_mnemonic',
            label: t('mnemonic'),
        },
        {
            key: 'master_register_mnemonic',
            label: t('master_register'),
        },
        {
            key: 'register_rank',
            label: t('rank'),
        },
        {
            key: 'register_purpose',
            label: t('purpose'),
        },
    ];

    return (
        <>
            <DataTable
                columns={columns}
                data={registers}
                loading={loading}
                rowKey={(item) => item.register_id}
                onRowClick={(item) =>
                    router.push(`/configuration/registers/${item.register_id}`)
                }
                actions={(item) => (
                    <>
                        <ViewButton
                            label={t('view')}
                            onClick={() => handleView(item)}
                        />

                        <Can action={CONFIGURATION_REGISTERS_ACTIONS.delete}>
                            <DeleteButton
                                label={t('remove')}
                                onClick={() => handleDelete(item)}
                            />
                        </Can>
                    </>
                )}
            />

            {isModalOpen && (
                <AddRegisterModal onClose={onCloseModal} onSuccess={refresh} />
            )}
            {isViewModalOpen && (
                <ViewRegisterFieldsModal
                    onClose={() => setIsViewModalOpen(false)}
                    data={viewData}
                />
            )}
            {showDeletePopup && (
                <ConfirmRemovePopup
                    onClose={() => {
                        setShowDeletePopup(false);
                        setSelectedRegister(null);
                    }}
                    onConfirm={handleConfirmDelete}
                    messageKey='confirm_delete_register'
                />
            )}
        </>
    );
}
