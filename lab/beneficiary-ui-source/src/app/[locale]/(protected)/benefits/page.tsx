"use client";

import Image from "next/image";
import { useState } from "react";
import { useLocale } from "next-intl";

import { AuthUtil } from '@/features/auth/components';
import { Pagination, SearchInput, FilterInput, Loading } from '@/components/shared';
import { prefixBasePath } from "@/shared/utils/path";
import { BenefitActionsDropdown, DeliveryDetails, BenefitsPageEmptyRow } from "@/features/disbursement/components";
import { DisbursementRecord } from "@/features/disbursement/types";
import { useDisbursementList } from "@/features/disbursement/hooks";

const modalBenefit = {
    programName: "Social Registry Upgrade",
    benefitCode: "Information Access",
    quantity: "1 Record",
    dateReceived: "24/09/2025",
    agent: { name: "John Doe", address: "123 Main St, City A" },
    deliveryDateTime: "24/09/2025 10:30 AM",
    address: "123 Main St, City A",
    mapImageUrl: "/map.png",
    evidenceImages: ["/e1.png", "/e2.png", "/e3.png"],
    biometricVerified: true,
    verificationType: "Fingerprint",
}

const PAGE_SIZE = 8;

export default function BenefitsPage() {
    const lang = useLocale();
    AuthUtil({ failedRedirectUrl: `/${lang}/login` });

    const [currentPage, setCurrentPage] = useState(1);

    const [searchQuery, setSearchQuery] = useState("");
    const [filterText, setFilterText] = useState("");

    const [selectedBenefit, setSelectedBenefit] = useState<DisbursementRecord | null>(null);
    const [isModalOpen, setIsModalOpen] = useState(false);

    const { disbursements, loading, totalItems, totalPages } = useDisbursementList(currentPage, PAGE_SIZE);

    const handleOpenModal = (benefit: DisbursementRecord) => {
        setSelectedBenefit(benefit);
        setIsModalOpen(true);
    };

    const handleProgramActionSelect = (action: string, benefit: DisbursementRecord) => {
        switch (action) {
            case "delivery-details":
                handleOpenModal(benefit);
                break;

            case "support":
                console.log("Redirect to support")
                break;

            default:
                console.warn("Unknown program action:", action);
        }
    };

    const startItem = totalItems === 0 ? 0 : (currentPage - 1) * PAGE_SIZE + 1;
    const endItem = Math.min(currentPage * PAGE_SIZE, totalItems);
    const emptyRowsCount = Math.max(PAGE_SIZE - disbursements.length, 0);

    if (loading) {
        return <Loading title={"Benefits"} height={"633px"} />
    }

    return (
        <>
            <div className="px-[50px] py-4 min-h-screen bg-white">
                <h1 className="text-[18px] font-[600] text-gray-800 mb-4">
                    Benefits
                </h1>

                <div className="bg-white rounded-[10px] drop-shadow-[0_4px_20px_rgba(0,0,0,0.25)] w-full overflow-hidden">
                    <div className="overflow-x-auto w-full">
                        <table className="w-full text-left border-collapse min-w-[700px]">
                            <thead>
                                <tr>
                                    <th colSpan={5}>
                                        <div className="flex justify-between items-center px-2 py-4">
                                            <span className="px-6 py-2 text-[#ED7C22] text-[18px] font-[600]">Benefits Received till Date</span>
                                            <div className="flex gap-4 pr-6">
                                                <FilterInput
                                                    value={filterText}
                                                    onChange={setFilterText}
                                                    placeholder="Filter"
                                                    className="w-50"
                                                    bgColor="bg-[#F5F5F5]"
                                                />
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
                                    </th>
                                </tr>

                                <tr className="bg-[#F5F5F5]">
                                    <th className="px-8 py-4 text-left text-black">
                                        <div className="flex items-center gap-0.5">
                                            Program Name
                                            <Image
                                                src={prefixBasePath("/updown_arrow.png")}
                                                alt="Sort"
                                                width={20}
                                                height={20}
                                                className="cursor-pointer opacity-40"
                                            />
                                        </div>
                                    </th>
                                    <th className="px-8 py-4 text-left text-black">
                                        <div className="flex items-center gap-0.5">
                                            Benefit Code
                                            <Image
                                                src={prefixBasePath("/updown_arrow.png")}
                                                alt="Sort"
                                                width={20}
                                                height={20}
                                                className="cursor-pointer opacity-40"
                                            />
                                        </div>
                                    </th>
                                    <th className="px-8 py-4 text-left text-black">Quantity</th>
                                    <th className="px-8 py-4 text-left text-black">
                                        <div className="flex items-center gap-0.5">
                                            Received Date
                                            <Image
                                                src={prefixBasePath("/updown_arrow.png")}
                                                alt="Sort"
                                                width={20}
                                                height={20}
                                                className="cursor-pointer opacity-40"
                                            />
                                        </div>
                                    </th>
                                    <th className="pl-7 pr-8 py-4 text-left text-black">Action</th>
                                </tr>
                            </thead>

                            <tbody>
                                {disbursements.map((d, index) => (
                                    <tr
                                        key={index}
                                        className={`transition-colors duration-150 ${index % 2 === 0 ? "bg-white" : "bg-[#F5F5F5]"}`}
                                    >
                                        <td className="px-8 py-3 text-black font-medium">{d.program_mnemonic}</td>
                                        <td className="px-8 py-3 text-black">{d.benefit_code}</td>
                                        <td className="px-8 py-3 text-black">{d.disbursement_quantity} {d.measurement_unit}</td>
                                        <td className="px-8 py-3 text-black">{d.disbursement_schedule_date}</td>
                                        <td className="px-7 py-3 text-[16px] font-[400] text-black">
                                            <BenefitActionsDropdown
                                                rowIndex={index}
                                                totalRows={disbursements.length}
                                                onActionSelect={(action) => handleProgramActionSelect(action, d)}
                                            />
                                        </td>
                                    </tr>
                                ))}

                                {[...Array(emptyRowsCount)].map((_, i) => (
                                    <BenefitsPageEmptyRow key={`empty-${i}`} index={disbursements.length + i} />
                                ))}
                            </tbody>
                        </table>
                    </div>

                    {!loading && totalItems > 0 && (
                        <div className="flex items-center gap-6 px-8 py-4 text-sm text-black">
                            <Pagination currentPage={currentPage} totalPages={totalPages} onPageChange={setCurrentPage} />
                            <div className="text-gray-600">
                                Showing {startItem}-{endItem} of {totalItems} Benefits
                            </div>
                        </div>
                    )}
                </div>
            </div>
            {isModalOpen && selectedBenefit && (
                <DeliveryDetails
                    benefit={modalBenefit}
                    onClose={() => setIsModalOpen(false)}
                />
            )}
        </>
    );
}
