"use client";
import { useState } from "react";
import { useLocale } from "next-intl";

import { Pagination, SearchInput, FilterInput } from '@/components/shared';
import { usePagination } from "@/shared/hooks/usePagination";
import { AuthUtil } from '@/features/auth/components';
import { ApplicationActionDropdown, ApplicationProgress } from "@/features/program/components";
import ApplicationDetails from "@/features/program/components/ApplicationDetails";

export interface Application {
    applicationName: string;
    applicationId: string;
    description: string;
    status: string;
    date: string;
}

export const applicationsData: Application[] = [
    // --- Social Welfare ---
    {
        applicationName: "Social Registry",
        applicationId: "1042504100",
        description: "The Social Registry program provides a centralized platform to track citizens' participation in social welfare initiatives. It records eligibility, applications, and updates across various welfare schemes, ensuring transparency and timely assistance. Users can submit updates, request benefits, and track the status of their applications, while authorities can monitor coverage, analyze data, and optimize social program delivery.",
        status: "Progress",
        date: "01/10/2025"
    },
    {
        applicationName: "Income Tax Assistance",
        applicationId: "1042504101",
        description: "This program guides citizens through income tax registration, filing, and compliance. It maintains records of taxpayer applications, deductions, and refunds. Beneficiaries can submit updates, track filings, and request support, while government agencies use the data to monitor compliance, prevent errors, and plan fiscal policies effectively.",
        status: "Pending",
        date: "02/10/2025"
    },
    {
        applicationName: "Caste Certificate Issuance",
        applicationId: "1042504102",
        description: "The Caste Certificate program allows eligible citizens to apply, update, and verify caste-based documentation. It tracks applications, approvals, and modifications, providing transparency and accountability. Citizens can request updates, monitor progress, and access certificate services efficiently, while authorities manage verification and reporting centrally.",
        status: "Applied",
        date: "03/10/2025"
    },
    {
        applicationName: "Electricity Subsidy Program",
        applicationId: "1042504103",
        description: "This program manages applications for electricity connections, subsidies, and bill assistance for households. It maintains detailed records of usage, eligibility, and support provided. Beneficiaries can update account information, request new connections, and track their subsidy status, while authorities optimize resource allocation and monitor energy distribution effectively.",
        status: "Pending",
        date: "04/10/2025"
    },
    {
        applicationName: "Voter Registry",
        applicationId: "1042504104",
        description: "The Voter Registry program maintains citizen enrollment, eligibility verification, and updates for voting purposes. It ensures accurate record-keeping and allows citizens to update personal information, verify registration, and access election-related notifications. Authorities use this system to maintain fair, transparent, and inclusive electoral processes.",
        status: "Progress",
        date: "05/10/2025"
    },
    {
        applicationName: "Unemployment Registry",
        applicationId: "1042504105",
        description: "This program tracks citizens seeking employment assistance, vocational training, and unemployment benefits. It records applications, program participation, and eligibility verification. Users can request updates, apply for support programs, and track progress, while authorities analyze labor data, plan workforce initiatives, and ensure effective allocation of resources.",
        status: "Applied",
        date: "06/10/2025"
    },
    {
        applicationName: "Disability Registry",
        applicationId: "1042504106",
        description: "The Disability Registry program records applications, certifications, and benefits for citizens with disabilities. It allows users to update personal information, track eligibility, and request support services. Authorities use the data to ensure inclusive program delivery, monitor accessibility initiatives, and allocate resources efficiently for disabled citizens.",
        status: "Pending",
        date: "07/10/2025"
    },

    // --- Education ---
    {
        applicationName: "Education Aid",
        applicationId: "1042504107",
        description: "The Education Aid program provides financial support and scholarship opportunities to students across all levels of education. It maintains records of applications, eligibility, and awards. Beneficiaries can update their educational information, apply for scholarships, and track the status of their applications. Authorities monitor participation, plan initiatives, and ensure equitable access to educational resources.",
        status: "Pending",
        date: "08/10/2025"
    },
    {
        applicationName: "School Supplies Distribution",
        applicationId: "1042504108",
        description: "This program ensures that students from low-income households receive necessary educational materials, including books, uniforms, and stationery. It tracks applications, approvals, and delivery status. Students and parents can submit requests, update details, and check progress, while authorities manage distribution and maintain transparency in program delivery.",
        status: "Approved",
        date: "09/10/2025"
    },
    {
        applicationName: "Vocational Training Program",
        applicationId: "1042504109",
        description: "The Vocational Training Program provides skill development and training opportunities to enhance employability. It tracks applications, course enrollments, and completion status. Participants can update profiles, apply for courses, and monitor progress. Authorities can evaluate program effectiveness, optimize training resources, and ensure skills development aligns with workforce needs.",
        status: "Progress",
        date: "10/10/2025"
    },
    {
        applicationName: "Higher Education Scholarships",
        applicationId: "1042504114",
        description: "This program offers scholarships for higher education to deserving students. It tracks applications, eligibility, and disbursement of funds. Beneficiaries can update academic information, submit scholarship requests, and monitor approval status, while authorities ensure fair allocation and transparency in scholarship distribution.",
        status: "Pending",
        date: "15/10/2025"
    },

    // --- Agriculture ---
    {
        applicationName: "Crop Subsidy Program",
        applicationId: "1042504110",
        description: "The Crop Subsidy Program provides financial assistance to farmers for cultivating approved crops. It maintains detailed records of applications, approvals, and disbursements. Farmers can submit updates, track subsidy payments, and access guidance for eligible crops. Authorities monitor agricultural productivity, allocate resources, and ensure timely support to the farming community.",
        status: "Applied",
        date: "11/10/2025"
    },
    {
        applicationName: "Irrigation Support",
        applicationId: "1042504111",
        description: "This program helps farmers access irrigation facilities, including water allocation, equipment subsidies, and maintenance support. It tracks applications, usage, and updates. Beneficiaries can request assistance, update records, and monitor progress, while authorities plan resources, maintain equitable water distribution, and optimize agricultural output.",
        status: "Pending",
        date: "12/10/2025"
    },
    {
        applicationName: "Fertilizer Subsidy",
        applicationId: "1042504112",
        description: "The Fertilizer Subsidy program provides farmers with subsidized access to fertilizers to enhance crop yields. It tracks applications, disbursements, and updates to ensure timely delivery. Beneficiaries can submit requests, monitor status, and update farm details. Authorities use the data to plan resource allocation, prevent misuse, and support sustainable agricultural practices.",
        status: "Approved",
        date: "13/10/2025"
    },
    {
        applicationName: "Agricultural Insurance Program",
        applicationId: "1042504113",
        description: "This program offers insurance coverage to farmers against crop failures, natural disasters, and other risks. It tracks applications, policy issuance, and claim settlements. Farmers can submit updates, track claims, and request support. Authorities analyze data to improve risk management, plan interventions, and ensure financial protection for the farming community.",
        status: "Progress",
        date: "14/10/2025"
    },
    {
        applicationName: "Organic Farming Initiative",
        applicationId: "1042504115",
        description: "The Organic Farming Initiative supports farmers transitioning to organic practices. It provides training, subsidies, and certification assistance. Farmers can update their farm details, track subsidy requests, and monitor certification progress. Authorities oversee program compliance, promote sustainable agriculture, and encourage environmentally friendly farming practices.",
        status: "Pending",
        date: "16/10/2025"
    }
];


export const getStatusClasses = (status: string) => {
    switch (status.toLowerCase()) {
        case "applied":
            return { bg: "bg-[rgba(51,153,255,0.2)]", text: "text-[#3399FF]" };
        case "progress":
            return { bg: "bg-[rgba(0,183,101,0.2)]", text: "text-[#00B765]" };
        case "pending":
            return { bg: "bg-[rgba(237,124,34,0.2)]", text: "text-[#ED7C22]" };
        case "approved":
            return { bg: "bg-[rgba(0,183,101,0.2)]", text: "text-[#00B765]" };
        case "rejected":
            return { bg: "bg-[rgba(237,124,34,0.2)]", text: "text-[#ED7C22]" };
        default:
            return { bg: "bg-gray-100", text: "text-gray-800" };
    }
};


export default function ApplicationsPage() {
    const lang = useLocale();
    AuthUtil({ failedRedirectUrl: `/${lang}/login` });

    const { currentPage, setCurrentPage, totalPages, currentItems } = usePagination(applicationsData, 8);

    const [searchQuery, setSearchQuery] = useState("");
    const [filterText, setFilterText] = useState("");

    const [selectedApplication, setSelectedApplication] = useState<Application | null>(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [activeModal, setActiveModal] = useState<"details" | "progress" | null>(null);


    const handleActionSelect = (action: string, application: Application) => {
        setSelectedApplication(application);
        if (action === "view-details") {
            setActiveModal("details");
            setIsModalOpen(true);
        } else if (action === "progress") {
            setActiveModal("progress");
            setIsModalOpen(true);
        }
    };

    return (
        <>
            <div className="px-[50px] py-4 min-h-screen bg-white">
                <h1 className="text-[18px] font-[600] text-gray-800 mb-4">
                    Applications
                </h1>

                <div className="bg-white rounded-[10px] drop-shadow-[0_4px_20px_rgba(0,0,0,0.25)] w-full overflow-hidden">
                    <div className="overflow-x-auto w-full">
                        <table className="w-full text-left border-collapse min-w-[700px]">
                            <thead>
                                <tr>
                                    <th colSpan={5}>
                                        <div className="flex justify-between items-center px-2 py-4">
                                            <span className="px-6 py-2 text-[#ED7C22] text-[20px] font-[600]">My Applications</span>
                                            <div className="flex gap-4 px-6">
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
                                    <th className="px-8 py-3 text-left text-black">Application Name</th>
                                    <th className="px-8 py-3 text-left text-black">Application ID</th>
                                    <th className="px-8 py-3 text-left text-black">Status</th>
                                    <th className="px-8 py-3 text-left text-black">Date</th>
                                    <th className="px-8 py-3 text-left text-black">Actions</th>
                                </tr>
                            </thead>

                            <tbody>
                                {currentItems.map((application, index) => (
                                    <tr
                                        key={index}
                                        className={`transition-colors duration-150 ${index % 2 === 0 ? "bg-white" : "bg-[#F5F5F5]"}`}
                                    >
                                        <td className="px-8 py-3 text-black font-medium">{application.applicationName}</td>
                                        <td className="px-8 py-3 text-black">{application.applicationId}</td>
                                        <td className="px-8 py-3">
                                            <span
                                                className={`px-2 py-1 rounded-full text-xs font-semibold ${getStatusClasses(application.status).bg
                                                    } ${getStatusClasses(application.status).text}`}
                                            >
                                                {application.status}
                                            </span>
                                        </td>
                                        <td className="px-8 py-3 text-black">{application.date}</td>
                                        <td className="px-8 py-3">
                                            <ApplicationActionDropdown
                                                rowIndex={index}
                                                totalRows={currentItems.length}
                                                onActionSelect={(action) => handleActionSelect(action, application)}
                                            />
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
                        <div className="text-gray-600 text-sm">
                            Showing{" "}
                            {Math.min((currentPage - 1) * 8 + 1, applicationsData.length)}–
                            {Math.min(currentPage * 8, applicationsData.length)} of {applicationsData.length}
                        </div>
                    </div>
                </div>
            </div>
            {isModalOpen && selectedApplication && (
                <>
                    {activeModal === "details" && (
                        <ApplicationDetails
                            application={selectedApplication}
                            onClose={() => setIsModalOpen(false)}
                        />
                    )}

                    {activeModal === "progress" && (
                        <ApplicationProgress
                            onClose={() => setIsModalOpen(false)}
                            applicationName={selectedApplication.applicationName}
                        />
                    )}
                </>
            )}
        </>
    );
}
