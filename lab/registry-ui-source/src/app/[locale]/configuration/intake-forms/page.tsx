'use client';

import { useState } from 'react';
import { TopBar } from '@/components/shared';
import { useFetch, usePagination } from '@/shared/hooks';
import { useRuntimeConfig } from '@/context/RuntimeConfigContext';
import { useRbac } from '@/context/RbacContext';
import { useTranslations } from 'next-intl';
import { useAllIntakeForms } from '@/features/configuration/shared/hooks/useAllIntakeForms';
import { AddIntakeFormModal } from '@/features/configuration/intake-forms';
import { DataTable, DeleteButton } from '@/features/configuration/shared/components';
import { toast } from 'react-toastify';
import ConfirmRemovePopup from '@/features/configuration/shared/components/ConfirmRemovePopup';
import { useRouter } from '@/i18n/navigation';
import { CONFIGURATION_INTAKE_FORM_ACTIONS } from '@/features/configuration/shared/utils/configurationIntakeForm.actions';
import Can from '@/components/shared/Can';

const IntakeFormPage = () => {
    const t = useTranslations();
    const router = useRouter();
    const [currentPage, setCurrentPage] = useState(1);
    const [modalType, setModalType] = useState<'add' | 'edit' | 'view' | null>(null);
    const [showPopup, setShowPopup] = useState(false);
    const [selectedItem, setSelectedItem] = useState<any>(null);
    const { execute: deleteIntakeForm } = useFetch();

    const { config } = useRuntimeConfig();

    const { can } = useRbac();
    const canCreate = can(CONFIGURATION_INTAKE_FORM_ACTIONS.edit);

    const { intake_forms, pagination, loading, refresh } = useAllIntakeForms(currentPage, config.pageSize);

    const { pageStart, pageEnd, total } = usePagination({
        totalItems: pagination?.number_of_items || 0,
        currentPage: currentPage,
        pageSize: config.pageSize || 10,
        currentCount: intake_forms?.length || 0,
    });

    const handlePrev = () => {
        setCurrentPage((prev) => Math.max(1, prev - 1));
    };

    const handleNext = () => {
        setCurrentPage((prev) => prev + 1);
    };

    const proceedDelete = async (id: string) => {
        try {
            const result = await deleteIntakeForm('/api/configuration/intake-forms/delete-intake-form', {
                method: 'POST',
                body: JSON.stringify({ form_id: id })
            });

            if (result?.form_id) {
                toast.success(t('intake_form_deleted'));
                refresh();
            } else {
                toast.error(t('toast_intake_form_deletion_failed'));
            }
        } catch (error) {
            toast.error(t('toast_operation_failed'));
        }
    };

    const handleConfirmDelete = async () => {
        if (!selectedItem) return;

        await proceedDelete(selectedItem.form_id);

        setShowPopup(false);
        setSelectedItem(null);
    };

    const handleDelete = (intakeForm: any) => {
        setSelectedItem(intakeForm);
        setShowPopup(true);
    };

    const columns = [
        {
            key: 'form_mnemonic',
            label: t('form_mnemonic'),
        },
        {
            key: 'form_description',
            label: t('description'),
        },
        {
            key: 'register_mnemonic',
            label: t('register'),
        },
        {
            key: 'number_of_verifications',
            label: t('verifications'),
        },
    ];

    return (
        <>
            <TopBar
                breadcrumb={[{ label: t('intake_forms') }]}
                showFilters={false}
                showPagination
                showAddNewButton={canCreate}
                addNewButtonText={t('add_new_intake_form')}
                onAddNewButton={() => setModalType('add')}
                pageStart={pageStart}
                pageEnd={pageEnd}
                total={total}
                onPrev={handlePrev}
                onNext={handleNext}
            />

            <DataTable
                columns={columns}
                data={intake_forms || []}
                loading={loading}
                rowKey={(item) => item.form_id}
                onRowClick={(item) =>
                    router.push(`/configuration/intake-forms/${item.form_id}`)
                }
                actions={(item) => (
                    <Can action={CONFIGURATION_INTAKE_FORM_ACTIONS.edit}>
                        <DeleteButton
                            label={t('remove')}
                            onClick={() => handleDelete(item)}
                        />
                    </Can>
                )}
            />

            {showPopup && (
                <ConfirmRemovePopup
                    onClose={() => {
                        setShowPopup(false);
                        setSelectedItem(null);
                    }}
                    onConfirm={handleConfirmDelete}
                    messageKey='confirm_remove_intake_form'
                />
            )}

            {modalType === 'add' && (
                <AddIntakeFormModal
                    onClose={() => setModalType(null)}
                    onSuccess={() => {
                        refresh();
                    }}
                />
            )}
        </>
    );
};

export default IntakeFormPage;
