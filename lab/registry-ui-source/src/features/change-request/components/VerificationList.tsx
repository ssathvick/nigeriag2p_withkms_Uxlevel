import Image from "next/image";
import { Verification } from "@/features/change-request/types/change-request";
import { VerificationCard } from "@/features/change-request/components";
import { useTranslations } from "next-intl";
import { VERIFICATION_CHANGE_REQUEST_ACTIONS } from "../utils/verificationChangeRequest.actions";
import Can from "@/components/shared/Can";

interface Props {
    verifications: Verification[];
    showForm: boolean;
    onToggleForm: () => void;
    renderForm: () => React.ReactNode;
    isPending: boolean;
}

export default function VerificationList({
    verifications,
    showForm,
    onToggleForm,
    renderForm,
    isPending,
}: Props) {
    const t = useTranslations();
    return (
        <Can action={VERIFICATION_CHANGE_REQUEST_ACTIONS.view}>
            <div className="rounded-lg space-y-4">
                {isPending && (
                    <div className="flex justify-between bg-primary-first px-6 py-4 rounded-[10px] items-center">
                        <h4 className="text-[24px] font-semibold">
                            {t("verifications")}
                        </h4>

                        <Can action={VERIFICATION_CHANGE_REQUEST_ACTIONS.create}>
                            <button
                                onClick={onToggleForm}
                                className="flex items-center gap-2 text-[14px] px-4 py-1 rounded-[10px] bg-neutral-first text-neutral-second"
                            >
                                <span className="pt-0.5">{t("add")}</span>
                                <Image
                                    src="/images/common/plus.png"
                                    alt="Add"
                                    width={12}
                                    height={12}
                                    className="pb-0.5"
                                />
                            </button>
                        </Can>
                    </div>)}

                {showForm && renderForm()}

                <div className="space-y-3">

                    {verifications.map((v) => (
                        <VerificationCard key={v.verification_id} verification={v} />
                    ))}
                </div>
            </div>
        </Can>
    );
};
