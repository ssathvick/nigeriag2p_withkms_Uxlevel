"use client";

import { ActionDropdown } from "@/components/ui";

interface Props {
    onActionSelect: (action: string) => void;
    rowIndex: number;
    totalRows: number;
}

const benefitactions = [
    { slug: "delivery-details", label: "Delivery Details" },
    { slug: "support", label: "Support" }
];

export default function BenefitActionsDropdown({ onActionSelect, rowIndex, totalRows }: Props) {
    const shouldOpenUp = rowIndex >= totalRows - 4;
    return (
        <ActionDropdown
            actions={benefitactions}
            onActionSelect={onActionSelect}
            openUp={shouldOpenUp}
        />
    );
}
