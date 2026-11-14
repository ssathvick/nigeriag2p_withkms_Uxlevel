"use client";

interface EmptyRowProps {
    index: number;
}

export default function BenefitsPageEmptyRow({ index }: EmptyRowProps) {
    const rowClass = index % 2 === 0 ? "bg-white" : "bg-[#F5F5F5]";

    return (
        <tr className={`h-[51.7px] ${rowClass}`}>
            <td className="px-8 py-3"></td>
            <td className="px-8 py-3"></td>
            <td className="px-8 py-3"></td>
            <td className="px-8 py-3"></td>
            <td className="px-8 py-3"></td>
        </tr>
    );
}
