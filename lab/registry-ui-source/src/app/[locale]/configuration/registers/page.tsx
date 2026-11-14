'use client';

import { useState } from 'react';
import { TopBar } from '@/components/shared';
import { RegistersConfigView } from '@/features/configuration/registers';
import { useAllRegister } from '@/features/configuration/shared';
import { usePagination } from '@/shared/hooks';
import { useRuntimeConfig } from '@/context/RuntimeConfigContext';
import { useRbac } from '@/context/RbacContext';
import { CONFIGURATION_REGISTERS_ACTIONS } from '@/features/configuration/shared/utils/configurationRegisters.actions';
import { useTranslations } from 'next-intl';

const RegistersConfigurationPage = () => {
    const t = useTranslations();
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [currentPage, setCurrentPage] = useState(1);

    // Env. variable config
    const { config } = useRuntimeConfig();

    const { can } = useRbac();
    const canCreate = can(CONFIGURATION_REGISTERS_ACTIONS.create);

    const { registers, pagination, loading, refresh } = useAllRegister(currentPage, config.pageSize);

    const { pageStart, pageEnd, total } = usePagination({
        totalItems: pagination?.number_of_items || 0,
        currentPage: currentPage,
        pageSize: config.pageSize || 10,
        currentCount: registers.length,
    });

    const handlePrev = () => {
        setCurrentPage((prev) => Math.max(1, prev - 1));
    };

    const handleNext = () => {
        setCurrentPage((prev) => prev + 1);
    };

    return (
        <>
            <TopBar
                breadcrumb={[{ label: t('registers') }]}
                showFilters={false}
                showPagination
                showAddNewButton={canCreate}
                addNewButtonText={t('add_new_register')}
                onAddNewButton={() => setIsModalOpen(true)}
                pageStart={pageStart}
                pageEnd={pageEnd}
                total={total}
                onPrev={handlePrev}
                onNext={handleNext}
            />

            <RegistersConfigView
                registers={registers}
                loading={loading}
                refresh={refresh}
                onAddNewRegister={() => setIsModalOpen(true)}
                isModalOpen={isModalOpen}
                onCloseModal={() => setIsModalOpen(false)}
            />

        </>
    );
};

export default RegistersConfigurationPage;
