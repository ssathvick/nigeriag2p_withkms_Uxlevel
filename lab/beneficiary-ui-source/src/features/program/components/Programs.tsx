"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { useLocale } from "next-intl";

import { prefixBasePath } from "@/shared/utils/path";

import { Program } from "@/features/program/types/program";
import { SearchInput, Pagination } from "@/components/shared";
import {
    ApplyProgramForm,
    ProgramActionsDropdown,
    ProgramDetails,
    ProgramsPageEmptyRow,
    ProgramsPagePlaceholderRow
} from "@/features/program/components";

import { getColorForBenefit } from "@/features/program/utils"
import { usePrograms } from "@/features/program/hooks";

interface ProgramsProps {
    showMyPrograms: boolean;
    activeTab: "all" | "my";
    setActiveTab: (tab: "all" | "my") => void;
}

export default function Programs({ showMyPrograms, activeTab, setActiveTab }: ProgramsProps) {
    const lang = useLocale();
    const pageSize = 8;

    const [searchQuery, setSearchQuery] = useState("");
    const [currentPage, setCurrentPage] = useState(1);
    const [openForm, setOpenForm] = useState(false);
    const { programs, loading, totalPages, totalItems } = usePrograms(activeTab, currentPage, pageSize);
    const [selectedProgram, setSelectedProgram] = useState<Program | null>(null);
    const [openDetails, setOpenDetails] = useState(false);
    const router = useRouter();

    const emptyRowsCount = Math.max(pageSize - programs.length, 0);
    const startItem = totalItems === 0 ? 0 : (currentPage - 1) * pageSize + 1;
    const endItem = Math.min(currentPage * pageSize, totalItems);

    useEffect(() => {
        setCurrentPage(1);
    }, [activeTab]);

    const getActionButton = (status: string, program: Program) => {
        if (status === "Applied") {
            return <span className="px-1 py-1 text-[#3399FF] font-medium cursor-default">Applied</span>;
        }
        return (
            <button
                onClick={() => router.push(`/${lang}/programs/apply/${program.id}`)}
                className="bg-black text-white text-sm px-3 py-1 rounded-full font-semibold hover:bg-gray-800 transition"
            >
                Apply
            </button>
        );
    };

    const handleProgramActionSelect = (action: string, program: Program) => {
        switch (action) {
            case "view-details":
                setSelectedProgram(program);
                setOpenDetails(true);
                break;

            case "details-submited":
                console.log("Redirect to details submitted")
                break;

            case "progress":
                console.log("Redirect to progress")
                break;

            case "disbursement-history":
                console.log("Redirect to disbursement history")
                break;

            default:
                console.warn("Unknown program action:", action);
        }
    };

    return (
        <>
            <div className="bg-white rounded-[10px] drop-shadow-[0_4px_20px_rgba(0,0,0,0.25)] w-full">
                <div className="relative">
                    <div className="absolute inset-x-0 bottom-0 h-[6px] bg-[#F5F5F5]" />

                    <div className="flex items-center justify-between px-8 gap-4 flex-wrap relative z-10">
                        <div className="flex gap-2 pt-8">
                            <button
                                onClick={() => setActiveTab("all")}
                                className={`px-6 py-2 text-[18px] font-[600] rounded-t-[20px] transition-all ${activeTab === "all"
                                    ? "bg-[#ED7C22] text-white"
                                    : "bg-[#D9D9D999]/60 text-black/50"
                                    }`}
                            >
                                All Programs
                            </button>
                            <button
                                onClick={() => setActiveTab("my")}
                                className={`px-6 py-2 text-[18px] font-[600] rounded-t-[20px] transition-all ${activeTab === "my"
                                    ? "bg-[#ED7C22] text-white"
                                    : "bg-[#D9D9D999]/60 text-black/50"
                                    }`}
                            >
                                My Programs
                            </button>
                        </div>
                        <div className="flex justify-center py-6">
                            <SearchInput
                                onSearch={(val) => {
                                    setCurrentPage(1);
                                    setSearchQuery(val);
                                }}
                                placeholder="Search"
                                className="w-[200px]"
                            />
                        </div>
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table className="min-w-full border-collapse table-fixed">
                        <thead className="bg-[#F5F5F5] text-black text-[16px] font-[700]">
                            <tr>
                                <th className="px-8 py-3 text-left">Program Name</th>
                                <th className="px-8 py-3 text-left">
                                    <div className="flex items-center gap-0.5">
                                        Benefits
                                        <Image
                                            src={prefixBasePath("/updown_arrow.png")}
                                            alt="Sort"
                                            width={20}
                                            height={20}
                                            className="cursor-pointer opacity-40"
                                        />
                                    </div>
                                </th>
                                {showMyPrograms ? (
                                    <>
                                        <th className="px-8 py-3 text-left">
                                            <div className="flex items-center gap-0.5">
                                                Enrollment Date
                                                <Image
                                                    src={prefixBasePath("/updown_arrow.png")}
                                                    alt="Sort"
                                                    width={20}
                                                    height={20}
                                                    className="cursor-pointer opacity-40"
                                                />
                                            </div>
                                        </th>
                                        <th className="pl-7 pr-8 py-3 text-left">
                                            Action
                                        </th>
                                    </>
                                ) : (
                                    <th className="pl-9 pr-8 py-3 text-left">Action</th>
                                )}
                            </tr>
                        </thead>
                        <tbody>
                            {loading &&
                                [...Array(emptyRowsCount)].map((_, i) => (
                                    <ProgramsPagePlaceholderRow
                                        key={`empty-${i}`}
                                        index={i}
                                        variant={showMyPrograms ? "my" : "all"}
                                    />
                                ))
                            }
                            {programs.map((p, idx) => (
                                <tr
                                    key={p.id}
                                    className={`text-sm ${idx % 2 === 0 ? "bg-white" : "bg-black/5"}`}
                                >
                                    <td className="px-8 py-3 text-[16px] font-[400] text-black">{p.program_mnemonic}</td>
                                    <td className="px-8 py-3">
                                        <div className="flex flex-wrap gap-2">
                                            {p.benefit_codes.map((b) => {
                                                const { bg, text } = getColorForBenefit(b.benefit_code_mnemonic);
                                                return (
                                                    <span
                                                        key={b.id}
                                                        className={`px-3 py-1 rounded-full text-sm font-medium ${bg} ${text}`}
                                                    >
                                                        {b.benefit_code_mnemonic}
                                                    </span>
                                                );
                                            })}
                                        </div>
                                    </td>
                                    {showMyPrograms ? (
                                        <>
                                            <td className="px-8 py-3 text-[16px] font-[400] text-black">{p.enrolment_date}</td>
                                            <td className="px-7 py-3 text-[16px] font-[400] text-black">
                                                <ProgramActionsDropdown
                                                    rowIndex={idx}
                                                    totalRows={programs.length}
                                                    onActionSelect={(action) => handleProgramActionSelect(action, p)}
                                                />
                                            </td>
                                        </>
                                    ) : (
                                        <td className="px-8 py-3">{getActionButton(p.am_i_enrolled ? "Applied" : "NO", p)}</td>
                                    )}
                                </tr>
                            ))}
                            {!loading &&
                                [...Array(emptyRowsCount)].map((_, i) => (
                                    <ProgramsPageEmptyRow
                                        key={`empty-${i}`}
                                        index={programs.length + i}
                                        variant={showMyPrograms ? "my" : "all"}
                                    />
                                ))
                            }
                        </tbody>
                    </table>
                </div>

                <div className="flex items-center gap-6 px-8 py-4 text-sm text-black">
                    {loading ? (
                        <div className="text-gray-600 py-4.5">Loading programs...</div>
                    ) : totalItems === 0 ? (
                        <div className="text-gray-600 py-4.5">No programs found</div>
                    ) : (
                        <>
                            <Pagination
                                currentPage={currentPage}
                                totalPages={totalPages}
                                onPageChange={setCurrentPage}
                            />
                            <div className="text-gray-600">
                                Showing {startItem}-{endItem} of {totalItems} Programs
                            </div>
                        </>
                    )}
                </div>

            </div>
            {openDetails && selectedProgram && (
                <ProgramDetails
                    program={selectedProgram}
                    onClose={() => setOpenDetails(false)}
                />
            )}
            {openForm && selectedProgram && (
                <ApplyProgramForm
                    program={selectedProgram}
                    onClose={() => setOpenForm(false)} />
            )}
        </>
    );
}
