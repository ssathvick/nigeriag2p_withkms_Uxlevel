'use client';

import { useState } from 'react';
import { TopBar } from '@/components/shared';
import { useAllSemanticPatterns, useIncomingSemanticPattern } from '@/features/configuration/shared';
import { usePagination, useFetch } from '@/shared/hooks';
import { useRuntimeConfig } from '@/context/RuntimeConfigContext';
import { useTranslations } from 'next-intl';
import { IncomingSemanticPattern } from '@/features/configuration/shared/hooks/useAllSemanticPatterns';
import { toast } from 'react-toastify';
import { useRbac } from '@/context/RbacContext';
import { CONFIGURATION_SEMANTIC_PATTERNS_ACTIONS } from '@/features/configuration/shared/utils/configurationSemanticPatterns.actions';
import Can from '@/components/shared/Can';
import { DeleteButton, EditButton, ViewButton, DataTable } from '@/features/configuration/shared/components';
import ConfirmRemovePopup from '@/features/configuration/shared/components/ConfirmRemovePopup';
import { AddSemanticPatternModal, EditSemanticPatternModal, ViewSemanticPatternModal } from '@/features/configuration/ingest';

const SemanticPatternsPage = () => {
    const t = useTranslations();
    const [modalType, setModalType] = useState<'add' | 'edit' | 'view' | null>(null);
    const [currentPage, setCurrentPage] = useState(1);
    const [showPopup, setShowPopup] = useState(false);
    const [selectedItem, setSelectedItem] = useState<IncomingSemanticPattern | null>(null);

    const { config } = useRuntimeConfig();
    const { can } = useRbac();
    const { semanticPatterns, pagination, loading, refresh } = useAllSemanticPatterns(currentPage, config.pageSize);
    const { selectedSemanticPattern, fetchSemanticPattern } = useIncomingSemanticPattern();
    const { execute: deletePattern } = useFetch();

    const { pageStart, pageEnd, total } = usePagination({
        totalItems: pagination?.number_of_items || 0,
        currentPage: currentPage,
        pageSize: config.pageSize || 10,
        currentCount: semanticPatterns.length,
    });

    const handlePrev = () => {
        setCurrentPage((prev) => Math.max(1, prev - 1));
    };

    const handleNext = () => {
        setCurrentPage((prev) => prev + 1);
    };

    const handleView = async (pattern: IncomingSemanticPattern) => {
        const result = await fetchSemanticPattern(pattern.semantic_pattern_id);
        if (result) {
            setModalType('view');
        }
    };

    const handleUpdate = async (pattern: IncomingSemanticPattern) => {
        const result = await fetchSemanticPattern(pattern.semantic_pattern_id);
        if (result) {
            setModalType('edit');
        }
    };

    const proceedDelete = async (id: string) => {
        try {
            const result = await deletePattern('/api/configuration/ingest/delete-semantic-pattern', {
                method: 'POST',
                body: JSON.stringify({ semantic_pattern_id: id })
            });

            if (result?.semantic_pattern_id) {
                toast.success(t('toast_semantic_pattern_removed'));
                refresh();
            } else {
                toast.error(t('toast_semantic_pattern_remove_failed'));
            }
        } catch (error) {
            toast.error(t('toast_operation_failed'));
        }
    };

    const handleConfirmDelete = async () => {
        if (!selectedItem) return;

        await proceedDelete(selectedItem.semantic_pattern_id);

        setShowPopup(false);
        setSelectedItem(null);
    };

    const handleDelete = (pattern: IncomingSemanticPattern) => {
        setSelectedItem(pattern);
        setShowPopup(true);
    };

    const columns = [
        // {
        //     key: 'semantic_pattern_id',
        //     label: t('semantic_pattern_id'),
        // },
        {
            key: 'data_model_mnemonic',
            label: t('data_model_mnemonic'),
        },
        {
            key: 'register_mnemonic',
            label: t('register_mnemonic'),
        },
        {
            key: 'intake_form_mnemonic',
            label: t('intake_form_mnemonic'),
        },
    ];

    return (
        <>
            <TopBar
                breadcrumb={[{ label: t('ingest_configurations') }, { label: t('semantic_patterns') }]}
                showFilters={false}
                showPagination
                showAddNewButton={can(CONFIGURATION_SEMANTIC_PATTERNS_ACTIONS.create)}
                addNewButtonText={t('add_new_semantic_pattern')}
                onAddNewButton={() => setModalType('add')}
                pageStart={pageStart}
                pageEnd={pageEnd}
                total={total}
                onPrev={handlePrev}
                onNext={handleNext}
            />

            <DataTable
                columns={columns}
                data={semanticPatterns}
                loading={loading}
                rowKey={(item) => item.semantic_pattern_id}
                actions={(item) => (
                    <>
                        <ViewButton
                            label={t('view')}
                            onClick={() => handleView(item)}
                        />

                        <Can action={CONFIGURATION_SEMANTIC_PATTERNS_ACTIONS.edit}>
                            <EditButton
                                label={t('common.edit')}
                                onClick={() => handleUpdate(item)}
                            />
                        </Can>

                        <Can action={CONFIGURATION_SEMANTIC_PATTERNS_ACTIONS.edit}>
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
                    messageKey='confirm_remove_ingest_semantic_pattern'
                />
            )}

            {modalType === 'add' && (
                <AddSemanticPatternModal
                    onClose={() => setModalType(null)}
                    onSuccess={refresh}
                />
            )}

            {modalType === 'view' && (
                <ViewSemanticPatternModal
                    onClose={() => setModalType(null)}
                    data={selectedSemanticPattern}
                />
            )}

            {modalType === 'edit' && (
                <EditSemanticPatternModal
                    onClose={() => setModalType(null)}
                    initialData={selectedSemanticPattern}
                    onSuccess={refresh}
                />
            )}
        </>
    );
};

export default SemanticPatternsPage;
