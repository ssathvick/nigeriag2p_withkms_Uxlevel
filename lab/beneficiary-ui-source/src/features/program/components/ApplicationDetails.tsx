"use client";

import Modal from "@/components/ui/Modal";
import { getStatusClasses } from "@/app/[locale]/(protected)/applications/page"
export interface Application {
    applicationName: string;
    applicationId: string;
    description: string;
    status: string;
    date: string;
}
interface ApplicationDetailsProps {
    application: Application;
    onClose: () => void;
}

export default function ApplicationDetails({ application, onClose }: ApplicationDetailsProps) {
    const statusClasses = getStatusClasses(application.status);
    return (
        <Modal
            title={<span className="text-[#ED7C22] text-[24px]">Application Details</span>}
            onClose={onClose}
            width="800px"
            height="600px"
            sidebarWidth="25%"
            sidebarImage="/application_details.png"
        >
            <div className="space-y-5 px-10">
                <div>
                    <label className="block text-[16px] text-black/50 font-[600] mb-1">Application Name</label>
                    <div className="text-[16px] text-black font-[600]">{application.applicationName}</div>
                </div>

                <div className="flex gap-8">
                    <div>
                        <label className="block text-[16px] text-black/50 font-[600] mb-1">Date</label>
                        <div className="text-[16px] text-black font-[600]">{application.date}</div>
                    </div>

                    <div>
                        <label className="block text-[16px] text-black/50 font-[600] mb-1">Application ID</label>
                        <div className="text-[16px] text-black font-[600]">{application.applicationId}</div>
                    </div>

                    <div>
                        <label className="text-[16px] text-black/50 font-[600]">
                            Status:
                            <span
                                className={`ml-2 px-2 py-1 rounded-full text-sm font-semibold ${statusClasses.bg} ${statusClasses.text}`}
                            >
                                {application.status}
                            </span>
                        </label>

                    </div>
                </div>


                {application.description && (
                    <div>
                        <label className="block text-sm font-bold text-black mb-1">Description</label>
                        <p className="text-[16px] text-black font-normal leading-relaxed">
                            {application.description}
                        </p>
                    </div>
                )}
            </div>

            <div className="flex justify-start gap-4 w-full my-8 px-10">
                <button
                    onClick={onClose}
                    className="px-8 py-2 bg-gray-100 text-black rounded-[20px] hover:bg-gray-200 transition"
                >
                    CLOSE
                </button>
            </div>
        </Modal>
    );
}
