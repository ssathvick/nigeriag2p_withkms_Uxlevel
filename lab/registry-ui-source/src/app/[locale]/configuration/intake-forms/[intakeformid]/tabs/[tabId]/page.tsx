'use client';

import { useState } from 'react';
import { BreadcrumbBar, TopBar } from '@/components/shared';
import { useParams } from 'next/navigation';
import { useBreadcrumb } from '@/shared/hooks/useBreadcrumb';
import {
    ConfigDetailsSummary,
    DataTable,
    DeleteButton,
    EditButton,
    ViewButton,
} from '@/features/configuration/shared';

import { useRuntimeConfig } from '@/context/RuntimeConfigContext';
import { useFetch, usePagination } from '@/shared/hooks';
import { useRbac } from '@/context/RbacContext';
import { useTranslations } from 'next-intl';
import { toast } from 'react-toastify';
import { useIntakeFormTabById } from '@/features/configuration/shared/hooks/useIntakeFormTabById';
import { useAllIntakeFormTabSections } from '@/features/configuration/shared/hooks/useAllIntakeFormTabSections';
import { useIntakeFormById } from '@/features/configuration/shared/hooks/useIntakeFormById';
import ViewIntakeFormTabModal from '@/features/configuration/intake-forms/ViewIntakeFormTabModal';
import EditIntakeFormTabModal from '@/features/configuration/intake-forms/EditIntakeFormTabModal';
import AddIntakeFormTabSectionModal from '@/features/configuration/intake-forms/AddIntakeFormTabSectionModal';
import ViewIntakeFormTabSectionModal from '@/features/configuration/intake-forms/ViewIntakeFormTabSectionModal';
import EditIntakeFormTabSectionModal from '@/features/configuration/intake-forms/EditIntakeFormTabSectionModal';
import ConfirmRemovePopup from '@/features/configuration/shared/components/ConfirmRemovePopup';
import { CONFIGURATION_INTAKE_FORM_ACTIONS } from '@/features/configuration/shared/utils/configurationIntakeForm.actions';
import Can from '@/components/shared/Can';


const IntakeFormTabIdPage = () => {
    const t = useTranslations();
    const { intakeformid } = useParams<{ intakeformid: string }>();
    const { tabId } = useParams<{ tabId: string }>();
    const {
        tab,
        loading: tabLoading,
        refresh: tabrefresh
    } = useIntakeFormTabById(tabId);

    const {
        intake_form,
        loading: intakeformLoading,
    } = useIntakeFormById(intakeformid);

    const [modalType, setModalType] = useState<'add' | 'edit' | 'view' | null>(null);
    const [sectionModal, setSectionModal] = useState<'add' | 'edit' | 'view' | null>(null);
    const [selectedSection, setSelectedSection] = useState<any>(null);

    const [showPopup, setShowPopup] = useState(false);
    const [selectedItem, setSelectedItem] = useState<any>(null);
    const { execute: deleteIntakeFormTabSection } = useFetch();


    const { can } = useRbac();
    const canEdit = can(CONFIGURATION_INTAKE_FORM_ACTIONS.edit);
    const canCreate = can(CONFIGURATION_INTAKE_FORM_ACTIONS.edit);


    const breadcrumb = useBreadcrumb({
        rootItem: { label: t('intake_form'), href: '/configuration/intake-forms' },
        customItems: [
            { label: `${intake_form?.form_mnemonic || ''}`, href: `/configuration/intake-forms/${intakeformid}` },
            { label: `${tab?.tab_label || ''}`, href: `/configuration/intake-forms/${intakeformid}/tab/${tabId}` }
        ]
    });

    const [currentPage, setCurrentPage] = useState(1);
    const { config } = useRuntimeConfig();

    const { sections, refresh, pagination } = useAllIntakeFormTabSections(currentPage, config.pageSize, tabId);

    const { pageStart, pageEnd, total } = usePagination({
        totalItems: pagination?.number_of_items || 0,
        currentPage: currentPage,
        pageSize: config.pageSize || 10,
        currentCount: sections?.length || 0,
    });

    const handlePrev = () => {
        setCurrentPage(prev => Math.max(1, prev - 1));
    };

    const handleNext = () => {
        setCurrentPage(prev => prev + 1);
    };

    const proceedDelete = async (id: string) => {
        try {
            const result = await deleteIntakeFormTabSection('/api/configuration/intake-forms/delete-section', {
                method: 'POST',
                body: JSON.stringify({ tab_section_id: id })
            });

            if (result?.tab_section_id) {
                toast.success(t('intake_form_tab_section_deleted'));
                refresh();
            } else {
                toast.error(t('toast_intake_form_tab_section_deletion_failed'));
            }
        } catch (error) {
            toast.error(t('toast_operation_failed'));
        }
    };

    const handleConfirmDelete = async () => {
        if (!selectedItem) return;

        await proceedDelete(selectedItem.tab_section_id);

        setShowPopup(false);
        setSelectedItem(null);
    };

    const handleDelete = (intakeForm: any) => {
        setSelectedItem(intakeForm);
        setShowPopup(true);
    };

    const columns = [
        {
            key: 'section_mnemonic',
            label: t('section_mnemonic'),
        },
        {
            key: 'section_order',
            label: t('section_order'),
        },
        {
            key: 'section_id',
            label: t('section_id'),
        },
    ];

    return (
        <>
            <div className="pt-10 px-7.5 mb-6">
                <BreadcrumbBar breadcrumb={breadcrumb} />
            </div>

            <ConfigDetailsSummary
                title={tab?.tab_label || t('none')}
                description={tab?.tab_order}
                onEdit={
                    canEdit
                        ? () => setModalType('edit')
                        : undefined
                }
                onView={() => setModalType('view')}
            />

            <div className=" ml-4 mt-4 px-7.5">
                <div className="flex justify-between items-center h-14">


                    {/* TopBar */}
                    <div className="font-medium text-[20px]">{t('intake_form_tab_sections')}</div>
                    <div className="flex items-center h-full">
                        <TopBar
                            breadcrumb={[]}
                            showFilters={false}
                            showPagination={true}
                            showAddNewButton={canCreate}
                            addNewButtonText={t('add_new_section')}
                            onAddNewButton={() => setSectionModal('add')}
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
                data={sections || []}
                loading={tabLoading}
                rowKey={(item) => item.tab_section_id}
                actions={(item) => (
                    <>
                        <ViewButton
                            label={t('view')}
                            onClick={() => {
                                setSelectedSection(item);
                                setSectionModal('view');
                            }}
                        />
                        <Can action={CONFIGURATION_INTAKE_FORM_ACTIONS.edit}>
                            <EditButton
                                label={t('common.edit')}
                                onClick={() => {
                                    setSelectedSection(item);
                                    setSectionModal('edit');
                                }}
                            />
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
                        refresh();
                    }}
                    onConfirm={handleConfirmDelete}
                    messageKey='confirm_remove_intake_form_tab_section'
                />
            )}

            {modalType === 'view' && (
                <ViewIntakeFormTabModal
                    data={tab}
                    onClose={() => {
                        setModalType(null);
                        setSelectedItem(null);
                    }}
                />
            )}

            {modalType === 'edit' && (
                <EditIntakeFormTabModal
                    initialData={tab}
                    onClose={() => {
                        setModalType(null);
                        setSelectedItem(null);
                    }}
                    onSuccess={() => {
                        tabrefresh();
                    }}
                />
            )}

            {sectionModal === 'add' && (
                <AddIntakeFormTabSectionModal
                    tabId={tabId}
                    onClose={() => setSectionModal(null)}
                    onSuccess={() => {
                        refresh();
                    }}
                />
            )}

            {sectionModal === 'view' && (
                <ViewIntakeFormTabSectionModal
                    data={selectedSection}
                    onClose={() => {
                        setSectionModal(null);
                        setSelectedSection(null);
                    }}
                />
            )}

            {sectionModal === 'edit' && (
                <EditIntakeFormTabSectionModal
                    initialData={selectedSection}
                    onClose={() => {
                        setSectionModal(null);
                        setSelectedSection(null);
                    }}
                    onSuccess={() => {
                        refresh();
                    }}
                />
            )}
        </>
    );
};

export default IntakeFormTabIdPage;
