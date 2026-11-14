"use client";

import { ActionDropdown } from "@/components/ui";

interface Props {
    onActionSelect: (action: string) => void;
    rowIndex: number;
    totalRows: number;
}

const registryActions = [
    { slug: "request-registry-details", label: "Registry Details" },
    { slug: "request-address-change", label: "Request for Change Address" },
];

export default function RegistryActionsDropdown({ onActionSelect, rowIndex, totalRows }: Props) {
    const shouldOpenUp = rowIndex >= totalRows - 4;
    return (
        <ActionDropdown
            actions={registryActions}
            onActionSelect={onActionSelect}
            openUp={shouldOpenUp}
        />
    );
}
