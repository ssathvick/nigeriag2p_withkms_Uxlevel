"use client";
import ActionDropdown from "@/components/ui/ActionDropdown";

interface Props {
    onActionSelect: (action: string) => void;
    rowIndex: number;
    totalRows: number;
}

const applicationoptions = [
    { slug: "view-details", label: "View Details" },
    { slug: "progress", label: "Progress" },
];

export default function ApplicationActionDropdown({ onActionSelect, rowIndex, totalRows }: Props) {
    const shouldOpenUp = rowIndex >= totalRows - 4;
    return (
        <ActionDropdown
            actions={applicationoptions}
            onActionSelect={onActionSelect}
            openUp={shouldOpenUp}
        />
    );
}
