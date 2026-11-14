"use client";
import { useState } from "react";
import { useLocale } from "next-intl";
import { AuthUtil } from '@/features/auth/components';
import { usePagination } from "@/shared/hooks/usePagination";
import { Pagination, SearchInput } from "@/components/shared";
import { FileComplaintForm } from "@/features/grievance/components";
import { Complaint } from "@/features/grievance/types/complaint";

const myComplaints: Complaint[] = [
    { id: "1", number: "1001", status: "In Progress", subject: "Healthcare Service Issue", description: "Delay in updating medical records in the healthcare registry.", date: "2025-09-20 10:30 AM" },
    { id: "2", number: "1002", status: "Closed", subject: "Employment Registry Error", description: "Incorrect designation shown in the employment registry.", date: "2025-09-18 02:15 PM" },
    { id: "3", number: "1003", status: "In Progress", subject: "Housing Registry Complaint", description: "Unable to apply for the new housing scheme online.", date: "2025-09-19 09:45 AM" },
    { id: "4", number: "1004", status: "Closed", subject: "Education Registry", description: "My degree verification request is still pending.", date: "2025-09-17 11:00 AM" },
    { id: "5", number: "1005", status: "In Progress", subject: "Pension Registry", description: "Mismatch in my pension account details after update.", date: "2025-09-16 03:20 PM" },
    { id: "6", number: "1006", status: "Closed", subject: "Food Security Registry", description: "Ration card details not reflecting after verification.", date: "2025-09-15 08:50 AM" },
    { id: "7", number: "1007", status: "In Progress", subject: "Electricity Billing Issue", description: "Incorrect billing amount shown for last month.", date: "2025-09-21 01:10 PM" },
    { id: "8", number: "1008", status: "Closed", subject: "Voter Registration Update", description: "Unable to update address in voter registry before elections.", date: "2025-09-14 09:00 AM" },
];

export default function ComplaintsPage() {
    const lang = useLocale();
    AuthUtil({ failedRedirectUrl: `/${lang}/login` });

    const [showModal, setShowModal] = useState(false);
    const [searchQuery, setSearchQuery] = useState("");

    const filteredComplaints = myComplaints.filter(c =>
        c.subject.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.description.toLowerCase().includes(searchQuery.toLowerCase())
    );

    const itemsPerPage = 4;
    const { currentPage, setCurrentPage, totalPages, currentItems } = usePagination(filteredComplaints, itemsPerPage);

    const getStatusStyles = (status: string) => {
        switch (status) {
            case "Closed":
                return "bg-[#3399FF]/20 text-[#3399FF]";
            case "In Progress":
                return "bg-[#00B765]/20 text-[#00B765]";
            default:
                return "bg-[#ED7C22] text-white";
        }
    };

    return (
        <div className="px-[50px] py-4 min-h-screen bg-white">
            <h1 className="text-[18px] font-[600] text-gray-800 mb-4">
                Complaints
            </h1>

            <div className="bg-white overflow-hidden rounded-[10px] drop-shadow-[0_4px_20px_rgba(0,0,0,0.25)]">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between px-8 py-4 gap-2">
                    <span className="text-[20px] font-[600] text-[#ED7C22]">All Complaints</span>
                    <div className="flex gap-2 items-center">
                        <SearchInput
                            onSearch={(val) => {
                                setCurrentPage(1);
                                setSearchQuery(val);
                            }}
                            placeholder="Search"
                            className="w-[200px]"
                        />
                        <button
                            className="bg-black text-white px-4 py-1 rounded-[17px] shadow"
                            onClick={() => setShowModal(true)}
                        >
                            File a Complaint
                        </button>
                    </div>
                </div>

                <div className="flex flex-col divide-y-12 divide-white max-h-[500px] overflow-y-auto">
                    {currentItems.map((complaint) => (
                        <div key={complaint.id} className="bg-gray-100 w-full">
                            <div className="px-8 py-3">
                                <div className="flex items-center gap-3 flex-wrap mb-1">
                                    <span className="text-black/50 font-[400] text-[16px]">Complaint Number:</span>
                                    <span className="text-black font-[500] text-[16px]">{complaint.number}</span>

                                    <span
                                        className={`px-2 py-1 text-xs font-semibold rounded-[20px] ${getStatusStyles(complaint.status)
                                            }`}
                                    >
                                        {complaint.status === "Closed" ? "Resolved" : complaint.status}
                                    </span>

                                    {(complaint.status === "Open" || complaint.status === "Closed") && (
                                        <button className="px-2 py-0.5 text-xs font-medium bg-[#ED7C22] text-white hover:bg-[#d16b1c] rounded-[20px]">
                                            Reopen
                                        </button>
                                    )}
                                </div>

                                <div className="flex justify-start items-center gap-4 flex-wrap">
                                    <span className="text-black/50 font-[400] text-[16px]">Subject:</span>
                                    <h3 className="text-black font-[500] text-[16px]">{complaint.subject}</h3>
                                    <span className="text-[#3399FF] font-[500] text-[16px]">{complaint.date}</span>
                                </div>

                                <p className="text-[16px] text-black font-[400] mt-1">{complaint.description}</p>
                            </div>
                        </div>
                    ))}
                </div>

                <div className="flex items-center gap-6 px-8 py-4 text-sm text-black">
                    <Pagination
                        currentPage={currentPage}
                        totalPages={totalPages}
                        onPageChange={setCurrentPage}
                    />
                    <div className="text-gray-600">
                        Showing{" "}
                        {currentItems.length === 0 ? 0 : (currentPage - 1) * itemsPerPage + 1}–
                        {(currentPage - 1) * itemsPerPage + currentItems.length} of {filteredComplaints.length} complaints
                    </div>
                </div>
            </div>

            {showModal && <FileComplaintForm onClose={() => setShowModal(false)} />}
        </div>
    );
}
