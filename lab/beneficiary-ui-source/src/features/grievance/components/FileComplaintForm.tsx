"use client";
import { useState } from "react";

import Modal from "@/components/ui/Modal";
import Image from "next/image";
import { prefixBasePath } from "@/shared/utils/path";

interface FileComplaintModalProps {
    onClose: () => void;
}

export default function FileComplaintForm({ onClose }: FileComplaintModalProps) {
    const [to, setTo] = useState("");
    const [subject, setSubject] = useState("");
    const [complaintText, setComplaintText] = useState("");

    return (
        <Modal
            title={<span className="text-[#ED7C22] text-[24px]">File a Complaint</span>}
            onClose={onClose}
            width="800px"
            height="550px"
            sidebarWidth="25%"
            sidebarImage="/file_complaints.png"
        >
            <div className="space-y-5 px-10 flex-1 overflow-y-auto">
                <div>
                    <label className="block text-sm font-medium text-gray-700">To</label>
                    <input
                        placeholder="support@openg2p.com"
                        type="text"
                        className="w-full bg-gray-100 rounded-md px-4 py-2 text-[16px] text-black/50 focus:outline-none"
                        value={to}
                        onChange={(e) => setTo(e.target.value)}
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700">Subject</label>
                    <div className="relative">
                        <select
                            value={subject}
                            onChange={(e) => setSubject(e.target.value)}
                            className="appearance-none w-full bg-gray-100 rounded-md px-4 py-2 text-[16px] text-black/50 cursor-pointer border-0 focus:outline-none focus:ring-0"
                        >
                            <option value="">Select</option>
                            <option value="Healthcare">Healthcare</option>
                            <option value="Employment">Employment</option>
                            <option value="Housing">Housing</option>
                            <option value="Education">Education</option>
                            <option value="Pension">Pension</option>
                            <option value="Food Security">Food Security</option>
                        </select>
                        <div className="pointer-events-none absolute right-5 top-1/2 transform -translate-y-1/2">
                            <Image
                                src={prefixBasePath("/arrow_02.png")}
                                alt="Dropdown arrow"
                                width={20}
                                height={20}
                                className="w-4 h-4"
                            />
                        </div>
                    </div>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700">Complaints</label>
                    <textarea
                        placeholder="Type your complaint..."
                        value={complaintText}
                        onChange={(e) => setComplaintText(e.target.value)}
                        rows={5}
                        className="mt-1 block w-full rounded-md bg-gray-100 p-2 text-black focus:outline-none focus:ring-0"
                    />
                </div>
            </div>

            <div className="flex justify-start gap-3 mt-10 px-10">
                <button
                    onClick={onClose}
                    className="px-4 py-2 bg-gray-200 text-black rounded-[20px]"
                >
                    Cancel
                </button>
                <button
                    className="px-4 py-2 bg-black text-white rounded-[20px]"
                >
                    Submit
                </button>
            </div>
        </Modal>
    );
}
