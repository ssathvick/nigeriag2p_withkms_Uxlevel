import { useState } from "react";
import Image from "next/image";
import { useTranslations } from "next-intl";
import { useAuth } from "@/context/Authcontext";

interface Props {
    onSubmit: (observation: string, isApproved: boolean) => Promise<boolean>;
    onClose: () => void;
}

export default function VerificationForm({ onSubmit, onClose }: Props) {
    const t = useTranslations();
    const [observation, setObservation] = useState("");
    const [isApproved, setIsApproved] = useState(true);

    const { user } = useAuth();

    const handleSubmit = async () => {
        const success = await onSubmit(observation, isApproved);
        if (success) {
            setObservation("");
            setIsApproved(true);
            onClose();
        }
    };

    return (
        <div className="relative border border-primary-first rounded-[10px] p-6 text-sm space-y-3 bg-neutral-second">
            <button
                onClick={onClose}
                className="absolute top-4 right-4"
            >
                <Image
                    src="/images/common/close.png"
                    alt={t("close")}
                    width={22}
                    height={22}
                    className="opacity-70 hover:opacity-100"
                />
            </button>

            <div className="font-semibold text-neutral-first/50">
                {t("new_verification")}
            </div>

            <div className="flex items-center gap-3">
                <div className="w-10 h-10 relative">
                    <Image
                        src="/images/common/verified_person.png"
                        alt={t("verified_person")}
                        fill
                        className="rounded-full object-cover"
                    />
                </div>
                <div className="flex flex-col">
                    <span className="text-[20px] font-medium text-neutral-first">
                        {user.name}
                        <span className="ml-2 text-[14px] text-neutral-first/50">{t("you")}</span>
                    </span>
                    <span className="text-[14px] text-neutral-first/50">
                        {new Date().toLocaleString()}
                    </span>
                </div>
            </div>

            <div>
                <div className="text-[14px] font-medium text-neutral-first/50 mb-1">
                    {t("message")}
                </div>
                <textarea
                    value={observation}
                    onChange={(e) => setObservation(e.target.value)}
                    rows={1}
                    placeholder={t("type_your_message")}
                    className="w-full border border-black/25 rounded-[10px] p-2 text-sm resize-none focus:outline-none"
                />
            </div>

            <div className="flex items-center justify-between pt-3">
                <div className="flex items-center gap-6">
                    <CheckboxOption
                        label={t("ok")}
                        checked={isApproved}
                        onClick={() => setIsApproved(true)}
                    />
                    <CheckboxOption
                        label={t("not_ok")}
                        checked={!isApproved}
                        onClick={() => setIsApproved(false)}
                    />
                </div>

                <button
                    onClick={handleSubmit}
                    className="px-4 py-1.5 text-sm rounded-xl bg-neutral-first text-neutral-second"
                >
                    {t("submit")}
                </button>
            </div>
        </div>
    );
};

const CheckboxOption = ({
    label,
    checked,
    onClick,
}: {
    label: string;
    checked: boolean;
    onClick: () => void;
}) => (
    <label
        className="flex items-center gap-2 cursor-pointer"
        onClick={onClick}
    >
        <input type="checkbox" checked={checked} readOnly className="hidden" />
        <div
            className={`w-6 h-6 border rounded flex items-center justify-center ${checked ? "border-primary-second" : "border-secondary-third"
                }`}
        >
            {checked && (
                <Image src="/images/common/tick.png" alt="tick" width={16} height={16} />
            )}
        </div>
        <span className="text-neutral-first">{label}</span>
    </label>
);
