'use client';

import { useMemo, useState } from "react";
import Image from "next/image";
import { useTranslations } from "next-intl";
import {
    VerificationCard,
    VerificationForm
} from "@/features/change-request/components";
import { useVerifications } from "@/features/change-request/hooks";
import { IntakeFormSubmission } from "../types/intake-form";
import { VERIFICATION_INTAKE_FORM_ACTIONS } from "../utils/verificationIntakeForm.actions";
import Can from "@/components/shared/Can";

interface Props {
    submission_id: string;
    isPending: boolean;
}

export default function IntakeVerificationCard({ submission_id, isPending }: Props) {
    const t = useTranslations();
    const [showForm, setShowForm] = useState(false);

    // same as change request verifications but with intakeFormSubmissionId
    const {
        verifications,
        loadingVerifications,
        addVerification
    } = useVerifications(undefined, submission_id);

    return (
        <Can action={VERIFICATION_INTAKE_FORM_ACTIONS.view}>
            <div className="rounded-lg space-y-4">
                <div className="bg-primary-first px-6 py-4 rounded-[10px] flex justify-between items-center shadow-sm">
                    <h4 className="text-[24px] font-semibold text-neutral-first">
                        {t("verifications")}
                    </h4>
                    {isPending && (
                        <Can action={VERIFICATION_INTAKE_FORM_ACTIONS.create}>
                            <button
                                onClick={() => setShowForm(!showForm)}
                                className="flex items-center gap-2 text-[14px] px-4 py-1 rounded-[10px] bg-neutral-first text-neutral-second hover:bg-secondary-second-800 transition-colors"
                            >
                                <span>{t("add")}</span>
                                <Image
                                    src="/images/common/plus.png"
                                    alt="Add"
                                    width={12}
                                    height={12}
                                />
                            </button>
                        </Can>
                    )}
                </div>

                {showForm && (
                    <VerificationForm
                        onSubmit={async (obs, approved) => {
                            const success = await addVerification(obs, approved);
                            if (success) setShowForm(false);
                            return success;
                        }}
                        onClose={() => setShowForm(false)}
                    />
                )}

                <div className="space-y-3">
                    {loadingVerifications ? (
                        <div className="py-4 text-center text-neutral-first/50">Loading verifications...</div>
                    ) : (
                        verifications.map((v) => (
                            <VerificationCard key={v.verification_id} verification={v} />
                        ))
                    )}
                </div>
            </div>
        </Can>
    );
}
