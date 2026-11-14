import Image from "next/image";
import { Verification } from "@/features/change-request/types/change-request";
import { useTranslations } from "next-intl";
import { formatDateTime } from "@/shared/utils/dateUtils";

interface VerificationCardProps {
    verification: Verification;
}

export default function VerificationCard(props: VerificationCardProps) {
    const { verification } = props;
    const t = useTranslations();
    return (
        <div className="bg-secondary-second rounded-[10px] p-6 space-y-3">
            <div className="font-normal text-[14px] text-neutral-first/50">
                {t("verified_by")}
            </div>

            <div className="flex items-center gap-3">
                <div className="w-10 h-10 relative">
                    <Image
                        src="/images/common/verified_person.png"
                        alt="verified person"
                        fill
                        className="rounded-full object-cover"
                    />
                </div>
                <div className="flex flex-col">
                    <span className="text-[20px] font-medium text-neutral-first">
                        {verification.verified_by}
                    </span>
                    <span className="text-[14px] text-neutral-first/50 font-normal">
                        {formatDateTime(verification.verified_at)}
                    </span>
                </div>
            </div>

            <div>
                <div className="text-[14px] font-normal text-neutral-first/50 mb-1">
                    {t("message")}
                </div>
                <div className="text-[16px] text-neutral-first font-normal">
                    {verification.verification_observations}
                </div>
            </div>

            <div className="flex items-center gap-6 pt-2">
                <StatusIndicator
                    label={t("ok")}
                    isActive={verification.is_approved}
                />
                <StatusIndicator
                    label={t("not_ok")}
                    isActive={!verification.is_approved}
                />
            </div>
        </div>
    );
}

const StatusIndicator = ({
    label,
    isActive,
}: {
    label: string;
    isActive: boolean;
}) => (
    <div className="flex items-center gap-2 text-neutral-first">
        <div
            className={`w-6 h-6 border rounded flex items-center justify-center ${isActive ? "border-primary-second bg-neutral-second" : "border-secondary-third bg-neutral-second"
                }`}
        >
            {isActive && (
                <Image src="/images/common/tick.png" alt="tick" width={16} height={16} />
            )}
        </div>
        <span className="text-[14px] font-medium text-neutral-first">{label}</span>
    </div>
);
