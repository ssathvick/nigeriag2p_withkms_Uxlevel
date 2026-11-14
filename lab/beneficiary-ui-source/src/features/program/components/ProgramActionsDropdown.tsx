"use client";

import { ActionDropdown } from "@/components/ui";

interface Props {
    onActionSelect: (action: string) => void;
    rowIndex: number;
    totalRows: number;
}

const programActions = [
    { slug: "view-details", label: "View Details" },
    { slug: "details-submited", label: "Details Submitted" },
    { slug: "progress", label: "Progress" },
    { slug: "disbursement-history", label: "Disbursement History" },
];

export default function ProgramActionsDropdown({ onActionSelect, rowIndex, totalRows }: Props) {
    const shouldOpenUp = rowIndex >= totalRows - 4;
    return (
        <ActionDropdown
            actions={programActions}
            onActionSelect={onActionSelect}
            openUp={shouldOpenUp}
        />
    );
}
