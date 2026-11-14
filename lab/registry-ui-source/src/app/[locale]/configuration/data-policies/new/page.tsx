'use client';

import { useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { ArrowLeft } from 'lucide-react';
import { toast } from 'react-toastify';
import { useRouter } from '@/i18n/navigation';
import { TopBar } from '@/components/shared';
import { useFetch } from '@/shared/hooks';
import { useAllRegister } from '@/features/configuration/shared';
import { useRegisterRecordFields } from '@/features/configuration/shared/hooks/useRegisterRecordFields';
import {
    CustomDropdown,
    InputField,
    TextAreaField,
} from '@/features/configuration/shared/components';
import PolicyFilterExpressionBuilder from '@/features/configuration/data-policies/PolicyFilterExpressionBuilder';
import PolicyFilterPreview from '@/features/configuration/data-policies/PolicyFilterPreview';
import {
    createDefaultFilterRoot,
    serializeFilterExpression,
    validateFilterExpression,
    type FilterRootState,
} from '@/features/configuration/data-policies/policyFilterExpression';

const POLICY_TYPES = ['ALLOW', 'DENY'] as const;

export default function NewDataPolicyPage() {
    const t = useTranslations();
    const router = useRouter();
    const searchParams = useSearchParams();

    const { execute: addPolicy } = useFetch();
    const { registers, loading: registersLoading } = useAllRegister(1, 100);
    const initialRegisterId = searchParams.get('registerId') ||'';

    console.log('initialRegisterId', initialRegisterId);


    const [registerId, setRegisterId] = useState(initialRegisterId);
    const [policyMnemonic, setPolicyMnemonic] = useState('');
    const [policyDescription, setPolicyDescription] = useState('');
    const [policyType, setPolicyType] = useState<string>('ALLOW');
    const [filterRoot, setFilterRoot] = useState<FilterRootState>(createDefaultFilterRoot());
    const [saving, setSaving] = useState(false);

    const lockRegister = Boolean(initialRegisterId);
    const { fields, loading: fieldsLoading } = useRegisterRecordFields(registerId);

    useEffect(() => {
        setRegisterId(initialRegisterId);
    }, [initialRegisterId]);

    useEffect(() => {
        if (initialRegisterId || registersLoading || !registers?.length) return;
        setRegisterId((current) => current || registers[0].register_id);
    }, [initialRegisterId, registers, registersLoading]);

    useEffect(() => {
        setFilterRoot(createDefaultFilterRoot());
    }, [registerId]);

    const registerOptions = useMemo(
        () =>
            (registers || []).map((r) => ({
                label: r.register_mnemonic || r.register_id,
                value: r.register_id,
            })),
        [registers],
    );

    const policyTypeOptions = useMemo(
        () => POLICY_TYPES.map((type) => ({ label: type, value: type })),
        [],
    );

    const listHref = registerId
        ? `/configuration/data-policies?registerId=${encodeURIComponent(registerId)}`
        : '/configuration/data-policies';

    const handleCancel = () => {
        router.push(listHref);
    };

    const handleSubmit = async () => {
        if (!registerId) {
            toast.warn(t('register_required'));
            return;
        }
        if (!policyMnemonic.trim()) {
            toast.warn(t('policy_mnemonic_required'));
            return;
        }
        if (!validateFilterExpression(filterRoot)) {
            toast.warn(t('policy_filter_expression_required'));
            return;
        }

        setSaving(true);
        try {
            const result = await addPolicy('/api/configuration/data-policy/add-policy', {
                method: 'POST',
                body: JSON.stringify({
                    register_id: registerId,
                    policy_mnemonic: policyMnemonic.trim(),
                    policy_description: policyDescription.trim(),
                    policy_type: policyType,
                    policy_filter_expression: serializeFilterExpression(filterRoot, fields),
                }),
            });

            if (result?.policy_id) {
                toast.success(t('toast_policy_created'));
                router.push(`${listHref}${listHref.includes('?') ? '&' : '?'}created=1`);
            } else {
                toast.error(t('toast_policy_create_failed'));
            }
        } finally {
            setSaving(false);
        }
    };

    return (
        <>
            <TopBar
                breadcrumb={[
                    { label: t('data_policies'), href: '/configuration/data-policies' },
                    { label: t('add_policy') },
                ]}
                showFilters={false}
                showPagination={false}
                showAddNewButton={false}

            />

            <div className="mx-7.5 flex flex-col gap-5 pb-10 font-roboto">
                <div className="bg-neutral-second rounded-[10px] p-6 flex items-center justify-between gap-4">
                    <div className="flex items-center gap-4">
                        <button
                            type="button"
                            onClick={handleCancel}
                            className="w-9 h-9 rounded-[10px] bg-secondary-first hover:bg-secondary-second flex items-center justify-center transition-colors"
                            aria-label={t('cancel')}
                        >
                            <ArrowLeft size={20} className="text-neutral-first" />
                        </button>
                        <h1 className="text-lg font-semibold text-neutral-first m-0">
                            {t('add_policy')}
                        </h1>
                    </div>

                    <div className="flex items-center gap-3">
                        <button
                            type="button"
                            onClick={handleCancel}
                            disabled={saving}
                            className="px-5 h-8.5 rounded-[10px] bg-secondary-second text-neutral-first/70 text-sm font-semibold hover:bg-secondary-third transition-colors disabled:opacity-50"
                        >
                            {t('cancel')}
                        </button>
                        <button
                            type="button"
                            onClick={handleSubmit}
                            disabled={saving}
                            className="px-5 h-8.5 rounded-[10px] bg-neutral-first text-neutral-second text-sm font-semibold transition-colors shadow-lg disabled:opacity-50"
                        >
                            {t('save')}
                        </button>
                    </div>
                </div>

                <div className="bg-neutral-second rounded-[10px] p-6">
                    <h2 className="text-base font-semibold text-neutral-first mb-4">
                        {t('policy_details')}
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-3xl">
                    <CustomDropdown
                        label={t('register')}
                        options={registerOptions}
                        value={registerId}
                        onChange={setRegisterId}
                        loading={registersLoading}
                        placeholder={t('select_register')}
                        disabled={lockRegister}
                    />
                        <CustomDropdown
                            label={t('policy_type')}
                            options={policyTypeOptions}
                            value={policyType}
                            onChange={setPolicyType}
                        />
                        <div className="md:col-span-2">
                            <InputField
                                label={t('policy_mnemonic')}
                                value={policyMnemonic}
                                onChange={setPolicyMnemonic}
                                placeholder={t('enter_policy_mnemonic')}
                            />
                        </div>
                        <div className="md:col-span-2">
                            <TextAreaField
                                label={t('policy_description')}
                                value={policyDescription}
                                onChange={setPolicyDescription}
                                placeholder={t('enter_policy_description')}
                            />
                        </div>
                    </div>
                </div>

                <div className="bg-neutral-second rounded-[10px] p-6">
                    <h2 className="text-base font-semibold text-neutral-first mb-4">
                        {t('filter_rules')}
                    </h2>
                    {!registerId ? (
                        <p className="text-[16px] text-neutral-first/50">
                            {t('select_register_for_filter_fields')}
                        </p>
                    ) : (
                        <div className="grid grid-cols-1 xl:grid-cols-[minmax(0,1fr)_minmax(280px,340px)] gap-6 items-stretch">
                            <PolicyFilterExpressionBuilder
                                root={filterRoot}
                                fields={fields}
                                fieldsLoading={fieldsLoading}
                                onChange={setFilterRoot}
                            />
                            <div className="xl:sticky xl:top-4 flex flex-col min-h-full">
                                <PolicyFilterPreview root={filterRoot} fields={fields} />
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </>
    );
}
