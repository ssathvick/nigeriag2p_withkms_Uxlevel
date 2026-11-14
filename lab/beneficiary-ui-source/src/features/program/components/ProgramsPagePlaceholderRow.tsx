"use client";

interface PlaceholderRowProps {
    index: number;
    variant: "all" | "my";
}

export default function ProgramsPagePlaceholderRow({ index, variant }: PlaceholderRowProps) {
    const rowClass = index % 2 === 0 ? "bg-white" : "bg-[#F5F5F5]";

    if (variant === "all") {
        return (
            <tr className={`${rowClass} animate-pulse h-[50px]`}>
                <td className="px-8 py-3.5">
                    <div className="h-6 w-37 bg-gray-300 rounded" />
                </td>

                <td className="px-8 py-3.5">
                    <div className="flex flex-wrap gap-2">
                        <div className="h-6 w-15 bg-gray-300 rounded-full" />
                        <div className="h-6 w-15 bg-gray-300 rounded-full" />
                        <div className="h-6 w-15 bg-gray-300 rounded-full" />
                    </div>
                </td>

                <td className="px-8 py-3.5">
                    <div className="h-6 w-12 bg-gray-300 rounded-full" />
                </td>
            </tr>
        );
    }

    return (
        <tr className={`${rowClass} animate-pulse h-[50px]`}>
            <td className="px-8 py-3.5">
                <div className="h-6 w-48 bg-gray-300 rounded" />
            </td>

            <td className="px-8 py-3.5">
                <div className="flex flex-wrap gap-2">
                    <div className="h-6 w-15 bg-gray-300 rounded-full" />
                    <div className="h-6 w-15 bg-gray-300 rounded-full" />
                    <div className="h-6 w-15 bg-gray-300 rounded-full" />
                </div>
            </td>

            <td className="px-8 py-3.5">
                <div className="h-4 w-15 bg-gray-300 rounded" />
            </td>

            <td className="px-8 py-3.5">
                <div className="h-6 w-12 bg-gray-300 rounded-full" />
            </td>
        </tr>
    );
}
