"use client";

interface EmptyRowProps {
    index: number;
    variant: "all" | "my";
}

export default function ProgramsPageEmptyRow({ index, variant }: EmptyRowProps) {
    const rowClass = index % 2 === 0 ? "bg-white" : "bg-[#F5F5F5]";

    return (
        <tr className={`h-[52px] ${rowClass}`}>
            <td className="px-8 py-6"></td>
            <td className="px-8 py-6"></td>
            {variant === "my" && <td className="px-8 py-6"></td>}
            <td className="px-8 py-6"></td>
        </tr>
    );
}
