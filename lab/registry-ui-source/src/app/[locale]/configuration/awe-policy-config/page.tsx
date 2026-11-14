'use client';

import { useMemo, useState } from 'react';
import { TopBar } from '@/components/shared';
import { useFetch, usePagination } from '@/shared/hooks';
import { useRuntimeConfig } from '@/context/RuntimeConfigContext';
import { useRbac } from '@/context/RbacContext';
import { useTranslations } from 'next-intl';
import { toast } from 'react-toastify';
import Can from '@/components/shared/Can';
import ConfirmRemovePopup from '@/features/configuration/shared/components/ConfirmRemovePopup';
import { DeleteButton, EditButton, DataTable, ViewButton } from '@/features/configuration/shared/components';
import { useAllAwePolicyConfigurations, type AwePolicyConfiguration } from '@/features/configuration/shared/hooks/useAllAwePolicyConfigurations';
import { useAllRegister } from '@/features/configuration/shared/hooks/useAllRegister';
import { CONFIGURATION_AWE_POLICY_ACTIONS } from '@/features/configuration/shared/utils/configurationAwePolicy.actions';
import {
    AWE_POLICY_SCOPE_OPTIONS,
    getAwePolicyTypeLabelKey,
} from '@/features/configuration/awe-policy-config/constants';
import AddAwePolicyConfigurationModal from '@/features/configuration/awe-policy-config/AddAwePolicyConfigurationModal';
import EditAwePolicyConfigurationModal from '@/features/configuration/awe-policy-config/EditAwePolicyConfigurationModal';
import ViewAwePolicyConfigurationModal from '@/features/configuration/awe-policy-config/ViewAwePolicyConfigurationModal';

const AwePolicyConfigurationPage = () => {
    const t = useTranslations();
    const [modalType, setModalType] = useState<'add' | 'edit' | 'view' | null>(null);
    const [currentPage, setCurrentPage] = useState(1);
    const [showPopup, setShowPopup] = useState(false);
    const [selectedItem, setSelectedItem] = useState<AwePolicyConfiguration | null>(null);

    const { execute: deleteConfig } = useFetch();
    const { config } = useRuntimeConfig();
    const { can } = useRbac();
    const canCreate = can(CONFIGURATION_AWE_POLICY_ACTIONS.create);

    const pageSize = config.pageSize || 100;

    const { awePolicyConfigurations, pagination, loading, refresh } = useAllAwePolicyConfigurations(
        currentPage,
        pageSize
    );
    const { registers } = useAllRegister(1, 500);

    const registerMnemonicById = useMemo(() => {
        const map = new Map<string, string>();
        registers.forEach((r) => map.set(r.register_id, r.register_mnemonic));
        return map;
    }, [registers]);

    const scopeLabel = (scope: string) => {
        const key = AWE_POLICY_SCOPE_OPTIONS.find((o) => o.value === scope)?.labelKey;
        return key ? t(key) : scope;
    };

    const { pageStart, pageEnd, total } = usePagination({
        totalItems: pagination?.number_of_items || 0,
        currentPage,
        pageSize: config.pageSize || 10,
        currentCount: awePolicyConfigurations.length,
    });

    const proceedDelete = async (id: string) => {
        try {
            const result = await deleteConfig('/api/configuration/awe-policy-config/delete', {
                method: 'POST',
                body: JSON.stringify({ awe_policy_config_id: id }),
            });

            if (result?.error) {
                toast.error(t('awe_policy_configuration_deletion_failed'));
            } else {
                toast.success(t('awe_policy_configuration_deleted_successfully'));
                refresh();
            }
        } catch {
            toast.error(t('awe_policy_configuration_deletion_failed'));
        }
    };

    const handleDelete = (e: React.MouseEvent<HTMLButtonElement>, item: AwePolicyConfiguration) => {
        e.preventDefault();
        e.stopPropagation();
        setSelectedItem(item);
        setShowPopup(true);
    };

    const confirmDelete = async () => {
        if (!selectedItem) return;
        await proceedDelete(selectedItem.awe_policy_config_id);
        setShowPopup(false);
        setSelectedItem(null);
    };

    const columns = [
        {
            key: 'policy_scope',
            label: t('policy_scope'),
            render: (item: AwePolicyConfiguration) => scopeLabel(item.policy_scope),
        },
        {
            key: 'register_id',
            label: t('register_mnemonic'),
            render: (item: AwePolicyConfiguration) =>
                registerMnemonicById.get(item.register_id) ?? item.register_id,
        },
        {
            key: 'policy_type',
            label: t('policy_type'),
            render: (item: AwePolicyConfiguration) => {
                const labelKey = getAwePolicyTypeLabelKey(item.policy_type);
                return labelKey ? t(labelKey) : item.policy_type;
            },
        },
        {
            key: 'policy_key',
            label: t('policy_key'),
        },
    ];

    return (
        <>
            <TopBar
                breadcrumb={[{ label: t('awe_policy_configurations') }]}
                showFilters={false}
                showPagination
                showAddNewButton={canCreate}
                addNewButtonText={t('add_new_awe_policy_configuration')}
                onAddNewButton={() => setModalType('add')}
                pageStart={pageStart}
                pageEnd={pageEnd}
                total={total}
                onPrev={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
                onNext={() => setCurrentPage((prev) => prev + 1)}
            />

            <DataTable
                columns={columns}
                data={awePolicyConfigurations}
                loading={loading}
                rowKey={(item) => item.awe_policy_config_id}
                actions={(item) => (
                    <>
                        <ViewButton
                            label={t('view')}
                            onClick={() => {
                                setSelectedItem(item);
                                setModalType('view');
                            }}
                        />
                        <Can action={CONFIGURATION_AWE_POLICY_ACTIONS.edit}>
                            <EditButton
                                label={t('common.edit')}
                                onClick={() => {
                                    setSelectedItem(item);
                                    setModalType('edit');
                                }}
                            />
                        </Can>
                        <Can action={CONFIGURATION_AWE_POLICY_ACTIONS.delete}>
                            <DeleteButton label={t('remove')} onClick={(e) => handleDelete(e, item)} />
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
                    messageKey="confirm_remove_awe_policy_configuration"
                />
            )}

            {modalType === 'view' && (
                <ViewAwePolicyConfigurationModal
                    data={selectedItem}
                    registerLabel={
                        selectedItem
                            ? registerMnemonicById.get(selectedItem.register_id)
                            : undefined
                    }
                    onClose={() => {
                        setModalType(null);
                        setSelectedItem(null);
                    }}
                />
            )}

            {modalType === 'add' && (
                <AddAwePolicyConfigurationModal
                    onClose={() => setModalType(null)}
                    onSuccess={refresh}
                />
            )}

            {modalType === 'edit' && (
                <EditAwePolicyConfigurationModal
                    data={selectedItem}
                    onClose={() => {
                        setModalType(null);
                        setSelectedItem(null);
                    }}
                    onSuccess={refresh}
                />
            )}
        </>
    );
};

export default AwePolicyConfigurationPage;
