"use client";
import { useState } from "react";
import { useLocale } from "next-intl";
import Image from "next/image";

import { prefixBasePath } from '@/shared/utils/path';
import { Pagination, SearchInput } from '@/components/shared';
import { RegistryActionDropdown, RegistryDetails } from '@/features/registry/components';
import { AuthUtil } from '@/features/auth/components';
import { useRouter } from "next/navigation";


import { Registry } from "@/features/registry/types";
import { usePagination } from "@/shared/hooks/usePagination";

export const allRegistries: Registry[] = [
    {
        name: "Education Registry",
        id: "93847561029",
        date: "10/07/2025",
        action: "Apply",
        description: "The Education Registry provides a detailed and structured platform for tracking educational enrollment, academic performance, scholarship programs, training opportunities, and participation in educational initiatives. It ensures that every student's information, from primary school enrollment to higher education records, is accurately maintained. Government agencies, schools, and educational institutions can monitor student progress, allocate resources efficiently, and design policies to improve learning outcomes. Users can submit updates to their records, apply for scholarships or educational benefits, and track the status of their applications. All updates and actions are logged for transparency and accountability. Additionally, the registry supports strategic planning for educational initiatives, reporting on program success, and ensuring that benefits reach eligible students in a timely manner."
    },
    {
        name: "Social Registry",
        id: "19283746501",
        date: "12/06/2025",
        action: "Apply",
        description: "The Social Registry serves as a comprehensive platform for managing citizen participation in social welfare programs, including eligibility verification, applications, benefit distribution, and monitoring of outcomes. It maintains detailed records of households, individuals, and their interactions with welfare initiatives. Government agencies can use the data to identify vulnerable populations, allocate resources effectively, design new programs, and ensure transparency in social service delivery. Citizens can submit applications, request updates, and track their eligibility status. The registry also facilitates reporting, auditing, and evaluation, helping ensure that welfare programs reach intended beneficiaries efficiently and equitably."
    },
    {
        name: "Income Tax Registry",
        id: "84756392013",
        date: "05/08/2025",
        action: "Applied",
        description: "The Income Tax Registry provides a centralized system for managing all citizen and business tax-related records. It tracks tax filings, refunds, compliance status, and correspondence with tax authorities. Government agencies can monitor trends in tax payments, detect discrepancies, plan audits, and improve revenue collection. Citizens and businesses can submit tax returns, update their records, track refunds, and ensure compliance with tax regulations. All actions are logged for transparency, accountability, and auditing purposes. The registry ensures that tax-related processes are efficient, accurate, and accessible to eligible taxpayers."
    },
    {
        name: "Caste Certificate Registry",
        id: "56473829102",
        date: "22/07/2025",
        action: "Apply",
        description: "The Caste Certificate Registry is designed to manage issuance, verification, and record-keeping of caste certificates required for accessing government benefits. It tracks applications, verification steps, approvals, and notifications to ensure that eligible citizens receive certificates promptly. Government authorities can monitor applications, prevent fraud, and ensure fairness in allocation of caste-based benefits. Citizens can submit new applications, update personal details, and request corrections. The registry maintains detailed records of all actions to provide transparency and accountability while supporting planning and evaluation of caste-based welfare programs."
    },
    {
        name: "Electricity Registry",
        id: "56473829103",
        date: "25/05/2025",
        action: "Apply",
        description: "The Electricity Registry provides a detailed system for managing electricity connections, billing, subsidy programs, consumption tracking, and eligibility for government assistance. It ensures that households, businesses, and public institutions are accurately registered and receive the benefits they are entitled to. Government authorities can monitor energy usage, allocate subsidies efficiently, detect discrepancies, and design programs to improve energy access. Citizens can submit applications for new connections, report issues, and track subsidy approvals. All updates are recorded to ensure transparency, accountability, and effective delivery of energy programs."
    },
    {
        name: "Voter Registry",
        id: "38475619284",
        date: "28/04/2025",
        action: "Apply",
        description: "The Voter Registry maintains accurate and current electoral rolls, ensuring that eligible citizens can participate in elections. It tracks registrations, corrections, removals, and updates to voter information. Government agencies can monitor voter eligibility, prevent fraud, and facilitate efficient election planning. Citizens can submit new registrations, request updates, and verify their enrollment status. The system records all actions and changes to maintain transparency and accountability. It also supports reporting and analysis to improve electoral processes and ensure fair representation across regions."
    },
    {
        name: "Unemployment Registry",
        id: "84756392014",
        date: "15/05/2025",
        action: "Apply",
        description: "The Unemployment Registry tracks job seekers, applications for unemployment benefits, skill development programs, and placement services. It provides a comprehensive view of labor market needs, individual eligibility, and program effectiveness. Government agencies can monitor trends in employment, allocate resources for training and placement, and plan initiatives to reduce unemployment. Citizens can submit applications for benefits, update personal information, track progress, and access support programs. The registry records all activities for accountability, transparency, and analytical purposes, ensuring effective delivery of unemployment services."
    },
    {
        name: "Disability Registry",
        id: "93847561030",
        date: "18/04/2025",
        action: "Apply",
        description: "The Disability Registry maintains detailed records of persons with disabilities, tracking eligibility for programs, certifications, medical assessments, and support services. It provides a centralized platform for government agencies to manage assistance programs, monitor participation, and ensure equitable access to benefits. Citizens can submit applications, update records, request services, and track approvals. The registry logs all actions for transparency, accountability, and reporting. It also supports planning, evaluation, and auditing of programs aimed at improving the welfare, inclusion, and quality of life of persons with disabilities."
    },
    {
        name: "Agriculture Registry",
        id: "12938475640",
        date: "10/04/2025",
        action: "Apply",
        description: "The Agriculture Registry tracks farmers, agricultural programs, subsidies, crop support initiatives, and farm management services. It provides detailed information on eligibility, applications, approvals, and benefit distribution. Government agencies can monitor crop patterns, allocate resources efficiently, plan programs, and provide timely assistance to farmers. Citizens can submit applications for subsidies, update farm details, and track program approvals. All updates and actions are logged to maintain transparency and accountability while ensuring equitable access to agricultural programs."
    },
    { name: "Education Registry", id: "84756392041", date: "01/03/2025", action: "Apply", description: "The Education Registry provides a detailed and structured platform for tracking educational enrollment, academic performance, scholarship programs, training opportunities, and participation in educational initiatives. It ensures that every student's information, from primary school enrollment to higher education records, is accurately maintained. Government agencies, schools, and educational institutions can monitor student progress, allocate resources efficiently, and design policies to improve learning outcomes. Users can submit updates to their records, apply for scholarships or educational benefits, and track the status of their applications. All updates and actions are logged for transparency and accountability. Additionally, the registry supports strategic planning for educational initiatives, reporting on program success, and ensuring that benefits reach eligible students in a timely manner." },
    { name: "Social Registry", id: "84756392042", date: "05/02/2025", action: "Apply", description: "The Social Registry serves as a comprehensive platform for managing citizen participation in social welfare programs, including eligibility verification, applications, benefit distribution, and monitoring of outcomes. It maintains detailed records of households, individuals, and their interactions with welfare initiatives. Government agencies can use the data to identify vulnerable populations, allocate resources effectively, design new programs, and ensure transparency in social service delivery. Citizens can submit applications, request updates, and track their eligibility status. The registry also facilitates reporting, auditing, and evaluation, helping ensure that welfare programs reach intended beneficiaries efficiently and equitably." },
    { name: "Income Tax Registry", id: "84756392043", date: "28/01/2025", action: "Applied", description: "The Income Tax Registry provides a centralized system for managing all citizen and business tax-related records. It tracks tax filings, refunds, compliance status, and correspondence with tax authorities. Government agencies can monitor trends in tax payments, detect discrepancies, plan audits, and improve revenue collection. Citizens and businesses can submit tax returns, update their records, track refunds, and ensure compliance with tax regulations. All actions are logged for transparency, accountability, and auditing purposes. The registry ensures that tax-related processes are efficient, accurate, and accessible to eligible taxpayers." },
    { name: "Electricity Registry", id: "84756392044", date: "15/01/2025", action: "Apply", description: "The Electricity Registry provides a detailed system for managing electricity connections, billing, subsidy programs, consumption tracking, and eligibility for government assistance. It ensures that households, businesses, and public institutions are accurately registered and receive the benefits they are entitled to. Government authorities can monitor energy usage, allocate subsidies efficiently, detect discrepancies, and design programs to improve energy access. Citizens can submit applications for new connections, report issues, and track subsidy approvals. All updates are recorded to ensure transparency, accountability, and effective delivery of energy programs." },
    { name: "Voter Registry", id: "84756392045", date: "10/01/2025", action: "Apply", description: "The Voter Registry maintains accurate and current electoral rolls, ensuring that eligible citizens can participate in elections. It tracks registrations, corrections, removals, and updates to voter information. Government agencies can monitor voter eligibility, prevent fraud, and facilitate efficient election planning. Citizens can submit new registrations, request updates, and verify their enrollment status. The system records all actions and changes to maintain transparency and accountability. It also supports reporting and analysis to improve electoral processes and ensure fair representation across regions." },
    { name: "Unemployment Registry", id: "84756392046", date: "05/01/2025", action: "Apply", description: "The Unemployment Registry tracks job seekers, applications for unemployment benefits, skill development programs, and placement services. It provides a comprehensive view of labor market needs, individual eligibility, and program effectiveness. Government agencies can monitor trends in employment, allocate resources for training and placement, and plan initiatives to reduce unemployment. Citizens can submit applications for benefits, update personal information, track progress, and access support programs. The registry records all activities for accountability, transparency, and analytical purposes, ensuring effective delivery of unemployment services." },
    { name: "Disability Registry", id: "84756392047", date: "01/01/2025", action: "Apply", description: "The Disability Registry maintains detailed records of persons with disabilities, tracking eligibility for programs, certifications, medical assessments, and support services. It provides a centralized platform for government agencies to manage assistance programs, monitor participation, and ensure equitable access to benefits. Citizens can submit applications, update records, request services, and track approvals. The registry logs all actions for transparency, accountability, and reporting. It also supports planning, evaluation, and auditing of programs aimed at improving the welfare, inclusion, and quality of life of persons with disabilities." },
];

const myRegistries: Registry[] = allRegistries.map(r => ({ ...r, action: "Request for Update" }));



export default function RegistriesPage() {
    const lang = useLocale();
    AuthUtil({ failedRedirectUrl: `/${lang}/login` });
    const router = useRouter();

    const [activeTab, setActiveTab] = useState<"all" | "my">("all");
    const [searchQuery, setSearchQuery] = useState("");
    const [currentPage, setCurrentPage] = useState(1);
    const [openForm, setOpenForm] = useState(false);
    const [openDetails, setOpenDetails] = useState(false);
    const [selectedRegistry, setSelectedRegistry] = useState<Registry | null>(null);

    const registriesToShow = activeTab === "all" ? allRegistries : myRegistries;

    const filteredRegistries = registriesToShow.filter(r =>
        r.name.toLowerCase().includes(searchQuery.toLowerCase()) || r.id.includes(searchQuery)
    );

    const itemsPerPage = 8;
    const totalPages = Math.ceil(filteredRegistries.length / itemsPerPage);
    const currentItems = filteredRegistries.slice(
        (currentPage - 1) * itemsPerPage,
        currentPage * itemsPerPage
    );

    const getActionButton = (action: string, registry: Registry) => {
        if (action === "Applied") {
            return (
                <span className="px-1 py-1 text-[#3399FF] font-medium">
                    Applied
                </span>
            );
        }
        return (
            <button
                onClick={() => {
                    setSelectedRegistry(registry);
                    setOpenForm(true);
                    router.push(`/registries/${registry.id}/apply`);
                }}
                className="bg-black text-white text-sm px-3 py-1 rounded-full font-semibold hover:bg-gray-800 transition"
            >
                Apply
            </button>
        );
    };

    const handleActionSelect = (option: string, registry: Registry) => {
        switch (option) {
            case "view-details":
                setSelectedRegistry(registry);
                setOpenDetails(true);
                break;
            case "request-address-change":
                router.push(`/registries/${registry.id}/address-change`);
                break;
            case "request-registry-details":
                router.push(`/registries/${registry.id}/view-details`);
                break;
        }
    };

    return (
        <div className="px-[50px] py-4 min-h-screen bg-white">
            <h1 className="text-[18px] font-[600] text-gray-800 mb-4">
                Registries
            </h1>

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
                                All Registries
                            </button>
                            <button
                                onClick={() => setActiveTab("my")}
                                className={`px-6 py-2 text-[18px] font-[600] rounded-t-[20px] transition-all ${activeTab === "my"
                                    ? "bg-[#ED7C22] text-white"
                                    : "bg-[#D9D9D999]/60 text-black/50"
                                    }`}
                            >
                                My Registries
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
                    <table className="min-w-full border-collapse">
                        <thead className="bg-[#F5F5F5] text-black text-[16px] font-[700]">
                            <tr>
                                <th className="px-8 py-3 text-left w-[60%]">Registry Name</th>
                                <th className="px-8 py-3 text-left w-[24%]">
                                    <div className="flex items-center gap-0.5">
                                        {activeTab === "all" ? "Date" : "Date of Registry"}
                                        <Image
                                            src={prefixBasePath("/updown_arrow.png")}
                                            alt="Sort"
                                            width={20}
                                            height={20}
                                            className="cursor-pointer opacity-40"
                                        />
                                    </div>
                                </th>
                                <th className="px-8 py-3 text-left w-[16%]">
                                    {activeTab === "all" ? "Action" : "Request"}
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            {currentItems.map((r, idx) => (
                                <tr key={r.id} className={`${idx % 2 === 0 ? "bg-white" : "bg-black/5"}`}>
                                    <td className="px-8 py-3 text-[16px] font-[400] text-black">{r.name}</td>
                                    <td className="px-8 py-3 text-[16px] font-[400] text-black">{r.date}</td>
                                    <td className="px-8 py-3">
                                        {activeTab === "all" ? (
                                            getActionButton(r.action, r)
                                        ) : (
                                            <RegistryActionDropdown
                                                rowIndex={idx}
                                                totalRows={currentItems.length}
                                                onActionSelect={(option) => handleActionSelect(option, r)}
                                            />
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>

                </div>

                <div className="flex items-center gap-6 px-8 py-4 text-sm text-black">
                    <Pagination
                        currentPage={currentPage}
                        totalPages={totalPages}
                        onPageChange={setCurrentPage}
                    />
                    <div className="text-gray-600">
                        Showing {Math.min((currentPage - 1) * itemsPerPage + 1, filteredRegistries.length)}–
                        {Math.min(currentPage * itemsPerPage, filteredRegistries.length)} of {filteredRegistries.length}
                    </div>
                </div>

                {openDetails && selectedRegistry && (
                    <RegistryDetails
                        registry={selectedRegistry}
                        onClose={() => setOpenDetails(false)}
                    />
                )}
            </div>
        </div>
    );
}
