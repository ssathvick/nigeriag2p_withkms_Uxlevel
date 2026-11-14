'use client';

import { useState } from 'react';
import { BreadcrumbBar, TopBar } from '@/components/shared';
import { useParams } from 'next/navigation';
import { useBreadcrumb } from '@/shared/hooks/useBreadcrumb';
import {
    ConfigDetailsSummary,
    DataTable,
    DeleteButton,
} from '@/features/configuration/shared';

import { useRuntimeConfig } from '@/context/RuntimeConfigContext';
import { useFetch, usePagination } from '@/shared/hooks';
import { useRbac } from '@/context/RbacContext';
import { useTranslations } from 'next-intl';
import { useIntakeFormById } from '@/features/configuration/shared/hooks/useIntakeFormById';
import { useAllIntakeFormTabs } from '@/features/configuration/shared/hooks/useAllIntakeFormTabs';
import { useRouter } from '@/i18n/navigation';
import { toast } from 'react-toastify';
import { EditIntakeFormModal, ViewIntakeFormModal } from '@/features/configuration/intake-forms';
import AddIntakeFormTabModal from '@/features/configuration/intake-forms/AddIntakeFormTabModal ';
import ConfirmRemovePopup from '@/features/configuration/shared/components/ConfirmRemovePopup';
import { CONFIGURATION_INTAKE_FORM_ACTIONS } from '@/features/configuration/shared/utils/configurationIntakeForm.actions';
import Can from '@/components/shared/Can';


const IntakeFormIdPage = () => {
    const t = useTranslations();
    const router = useRouter();
    const { intakeformid } = useParams<{ intakeformid: string }>();
    const {
        intake_form,
        loading,
        refresh: editRefresh
    } = useIntakeFormById(intakeformid);

    const [modalType, setModalType] = useState<'add' | 'edit' | 'view' | null>(null);
    const [showPopup, setShowPopup] = useState(false);
    const [selectedItem, setSelectedItem] = useState<any>(null);
    const { execute: deleteIntakeFormTab } = useFetch();


    const { can } = useRbac();
    const canEdit = can(CONFIGURATION_INTAKE_FORM_ACTIONS.edit);
    const canCreate = can(CONFIGURATION_INTAKE_FORM_ACTIONS.edit);


    const breadcrumb = useBreadcrumb({
        rootItem: { label: t('intake_form'), href: '/configuration/intake-forms' },
        customItems: [
            { label: `${intake_form?.form_mnemonic || ''}`, href: `/configuration/intake-forms/${intakeformid}` }
        ]
    });

    const [currentPage, setCurrentPage] = useState(1);
    const { config } = useRuntimeConfig();

    const { intake_form_tabs, refresh, pagination } = useAllIntakeFormTabs(currentPage, config.pageSize, intakeformid);

    const { pageStart, pageEnd, total } = usePagination({
        totalItems: pagination?.number_of_items || 0,
        currentPage: currentPage,
        pageSize: config.pageSize || 10,
        currentCount: intake_form_tabs?.length || 0,
    });

    const handlePrev = () => {
        setCurrentPage(prev => Math.max(1, prev - 1));
    };

    const handleNext = () => {
        setCurrentPage(prev => prev + 1);
    };

    const proceedDelete = async (id: string) => {
        try {
            const result = await deleteIntakeFormTab('/api/configuration/intake-forms/delete-tab', {
                method: 'POST',
                body: JSON.stringify({ tab_id: id })
            });

            if (result?.tab_id) {
                toast.success(t('intake_form_tab_deleted'));
                editRefresh();
            } else {
                toast.error(t('toast_intake_form_tab_deletion_failed'));
            }
        } catch (error) {
            toast.error(t('toast_operation_failed'));
        }
    };

    const handleConfirmDelete = async () => {
        if (!selectedItem) return;

        await proceedDelete(selectedItem.tab_id);

        setShowPopup(false);
        setSelectedItem(null);
    };

    const handleDelete = (tab: any) => {
        setSelectedItem(tab);
        setShowPopup(true);
    };

    const columns = [
        {
            key: 'tab_id',
            label: t('tab_id'),
        },
        {
            key: 'tab_label',
            label: t('tab_label'),
        },
        {
            key: 'tab_order',
            label: t('tab_order'),
        },
    ];

    return (
        <>
            <div className="pt-10 px-7.5 mb-6">
                <BreadcrumbBar breadcrumb={breadcrumb} />
            </div>

            <ConfigDetailsSummary
                title={intake_form?.form_mnemonic || t('none')}
                description={intake_form?.form_description}
                extraInfo1={intake_form?.register_mnemonic || t('none')}
                onEdit={
                    canEdit
                        ? () => setModalType('edit')
                        : undefined
                }
                onView={() => setModalType('view')}
            />

            <div className=" ml-4 mt-4 px-7.5">
                <div className="flex justify-between items-center h-14">
                    <div className="font-medium text-[20px]">{t('intake_form_tabs')}</div>
                    <div className="flex items-center h-full">
                        <TopBar
                            breadcrumb={[]}
                            showFilters={false}
                            showPagination={true}
                            showAddNewButton={canCreate}
                            addNewButtonText={t('add_new_tab')}
                            onAddNewButton={() => setModalType('add')}
                            showSecondaryButton={false}
                            pageStart={pageStart}
                            pageEnd={pageEnd}
                            total={total}
                            onPrev={handlePrev}
                            onNext={handleNext}
                            showCapsule={false}
                        />
                    </div>
                </div>
            </div>

            <DataTable
                columns={columns}
                data={intake_form_tabs || []}
                loading={loading}
                rowKey={(item) => item.tab_id}
                onRowClick={(item) =>
                    router.push(`/configuration/intake-forms/${intakeformid}/tabs/${item.tab_id}`)
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
                    messageKey='confirm_remove_intake_form_tab'
                />
            )}

            {modalType === 'view' && (
                <ViewIntakeFormModal
                    data={intake_form}
                    onClose={() => {
                        setModalType(null);
                        setSelectedItem(null);
                    }}
                />
            )}

            {modalType === 'edit' && (
                <EditIntakeFormModal
                    initialData={intake_form}
                    onClose={() => {
                        setModalType(null);
                        setSelectedItem(null);
                    }}
                    onSuccess={() => {
                        editRefresh();
                    }}
                />
            )}

            {modalType === 'add' && (
                <AddIntakeFormTabModal
                    intakeFormId={intakeformid}
                    onClose={() => setModalType(null)}
                    onSuccess={() => {
                        refresh();
                    }}
                />
            )}
        </>
    );
};

export default IntakeFormIdPage;
