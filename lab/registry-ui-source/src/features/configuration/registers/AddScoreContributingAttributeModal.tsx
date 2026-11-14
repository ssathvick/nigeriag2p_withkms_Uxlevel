'use client';

import { useState } from 'react';
import { X } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { useFetch } from '@/shared/hooks';
import { toast } from 'react-toastify';

interface AddScoreContributingAttributeModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess?: () => void;
    scoreDefinitionId: string;
}

function parseComputationJson(raw: string): Record<string, unknown> | null {
    const trimmed = raw.trim();
    if (!trimmed) return {};
    try {
        const parsed = JSON.parse(trimmed) as unknown;
        if (parsed === null || typeof parsed !== 'object' || Array.isArray(parsed)) {
            return null;
        }
        return parsed as Record<string, unknown>;
    } catch {
        return null;
    }
}

export default function AddScoreContributingAttributeModal({
    isOpen,
    onClose,
    onSuccess,
    scoreDefinitionId,
}: AddScoreContributingAttributeModalProps) {
    const t = useTranslations();
    const { execute: createAttr } = useFetch();

    const [attributeName, setAttributeName] = useState('');
    const [attributeWeightage, setAttributeWeightage] = useState('0');
    const [computationRequired, setComputationRequired] = useState(false);
    const [computationValueJson, setComputationValueJson] = useState('{}');

    const handleSubmit = async () => {
        if (!attributeName.trim()) {
            toast.warn(t('attribute_name_required'));
            return;
        }
        let value: Record<string, unknown> = {};
        if (computationRequired) {
            const parsed = parseComputationJson(computationValueJson);
            if (parsed === null) {
                toast.error(t('invalid_json_computation_value'));
                return;
            }
            value = parsed;
        }
        const weightage = Number(attributeWeightage);
        if (Number.isNaN(weightage)) {
            toast.warn(t('attribute_weightage_invalid'));
            return;
        }

        const result = await createAttr(
            '/api/configuration/registers/score/attribute/create-score-contributing-attributes',
            {
                method: 'POST',
                body: JSON.stringify({
                    score_definition_id: scoreDefinitionId,
                    attribute_name: attributeName.trim(),
                    attribute_computation_required: computationRequired,
                    attribute_computation_value: value,
                    attribute_weightage: attributeWeightage,
                }),
            },
        );

        const created = result as { contributing_attribute_id?: string; error?: string } | null;
        if (created?.contributing_attribute_id && !created.error) {
            toast.success(t('toast_contributing_attribute_created'));
            setAttributeName('');
            setAttributeWeightage('0');
            setComputationRequired(false);
            setComputationValueJson('{}');
            onSuccess?.();
            onClose();
        } else {
            toast.error(t('toast_contributing_attribute_create_failed'));
        }
    };

    const handleCancel = () => {
        setAttributeName('');
        setAttributeWeightage('0');
        setComputationRequired(false);
        setComputationValueJson('{}');
        onClose();
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-neutral-first/80 z-50 flex items-center justify-center p-4">
            <div className="relative w-full max-w-200 max-h-[90vh] bg-primary-first rounded-[10px] overflow-hidden flex p-1">
                <div className="flex-1 w-full bg-neutral-second relative rounded-[10px] overflow-y-auto p-10 max-h-[90vh]">
                    <button
                        onClick={handleCancel}
                        className="absolute top-6 right-6 text-secondary-third hover:text-neutral-first/70 transition-colors"
                    >
                        <X size={40} strokeWidth={2} />
                    </button>

                    <h2 className="text-2xl font-bold text-primary-second mb-4">
                        {t('add_contributing_attribute')}
                    </h2>

                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-semibold text-neutral-first mb-1">
                                {t('attribute_name')}
                            </label>
                            <input
                                type="text"
                                value={attributeName}
                                onChange={(e) => setAttributeName(e.target.value)}
                                className="w-full px-4 py-2 border border-primary-second rounded-lg outline-none outline-1 outline-primary-second transition-all text-neutral-first/70 placeholder:text-secondary-third"
                            />
                        </div>

                        <div className="flex items-center gap-3">
                            <input
                                type="checkbox"
                                id="add_comp_req"
                                checked={computationRequired}
                                onChange={(e) => setComputationRequired(e.target.checked)}
                                className="h-4 w-4 rounded border-primary-second text-primary-second focus:ring-primary-second"
                            />
                            <label htmlFor="add_comp_req" className="text-sm font-semibold text-neutral-first">
                                {t('attribute_computation_required')}
                            </label>
                        </div>

                        {computationRequired && (
                            <div>
                                <label className="block text-sm font-semibold text-neutral-first mb-1">
                                    {t('attribute_computation_value_json')}
                                </label>
                                <textarea
                                    value={computationValueJson}
                                    onChange={(e) => setComputationValueJson(e.target.value)}
                                    rows={5}
                                    className="w-full px-4 py-2 border border-primary-second rounded-lg font-mono text-sm outline-none outline-1 outline-primary-second text-neutral-first/70"
                                />
                            </div>
                        )}

                        <div>
                            <label className="block text-sm font-semibold text-neutral-first mb-1">
                                {t('attribute_weightage')}
                            </label>
                            <input
                                type="number"
                                step="any"
                                value={attributeWeightage}
                                onChange={(e) => setAttributeWeightage(e.target.value)}
                                className="w-full px-4 py-2 border border-primary-second rounded-lg outline-none outline-1 outline-primary-second transition-all text-neutral-first/70"
                            />
                        </div>

                        <div className="flex gap-4 pt-4">
                            <button
                                onClick={handleCancel}
                                className="px-12 py-2.5 bg-secondary-third text-neutral-first rounded-[10px]"
                            >
                                {t('cancel')}
                            </button>
                            <button
                                onClick={handleSubmit}
                                className="px-12 py-2.5 bg-neutral-first text-neutral-second rounded-[10px]"
                            >
                                {t('save')}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
