"use client";

import Image from "next/image";
import Modal from "@/components/ui/Modal";
import { getStatusClasses } from "@/app/[locale]/(protected)/applications/page";
import { prefixBasePath } from "@/shared/utils/path";

export interface VerificationItem {
    label: string;
    passed: boolean;
}

export interface ApplicationStep {
    stepId: string;
    status: string;
    date: string;
    evaluator: string;
    description?: string;
    verifications?: VerificationItem[];
}

export default function ApplicationProgress({
    onClose,
    applicationName,
}: {
    onClose: () => void;
    applicationName: string;
}) {
    const steps: ApplicationStep[] = [
        {
            stepId: "O1",
            status: "Applied",
            date: "09/10/25",
            evaluator: "James George",
            description: "Applied successfully",
        },
        {
            stepId: "O2",
            status: "Pending",
            date: "10/10/25",
            evaluator: "James George",
            verifications: [
                { label: "ID verification check", passed: true },
                { label: "Address verification check (Address mismatch)", passed: false },
                { label: "Location verification check", passed: true },
                { label: "Contact number verification check", passed: true },
            ],
        },
        {
            stepId: "O3",
            status: "Pending",
            date: "11/10/25",
            evaluator: "Mary Elizabeth",
            verifications: [
                { label: "New address proof uploaded", passed: true },
                { label: "Address verification check", passed: true },
            ],
        },
        {
            stepId: "O4",
            status: "In Progress",
            date: "12/10/25",
            evaluator: "Mary Elizabeth",
            description: "Processing your application",
        },
    ];

    return (
        <Modal
            title={<span className="text-[#ED7C22] text-[24px]">Application Progress</span>}
            onClose={onClose}
            width="900px"
            height="700px"
            sidebarWidth="25%"
            sidebarImage="/application_details.png"
        >
            <div className="px-10 pt-4 space-y-8">
                <div>
                    <label className="block text-[16px] text-black/50 font-[600] mb-1">
                        Application Name
                    </label>
                    <div className="text-[18px] text-black font-[600]">{applicationName}</div>
                </div>

                <div className="space-y-5">
                    {steps.map((step) => {
                        const statusClasses = getStatusClasses(step.status);
                        return (
                            <div key={step.stepId} className="relative">
                                <div className="flex justify-between items-start mb-2">
                                    <div className="flex items-center gap-3">
                                        <span className="text-gray-400 font-bold text-lg">{step.stepId}</span>
                                        <span
                                            className={`px-2 py-1 rounded-full text-sm font-semibold ${statusClasses.bg} ${statusClasses.text}`}
                                        >
                                            {step.status}
                                        </span>
                                        <span className="text-gray-500 text-sm">{step.date}</span>
                                    </div>
                                    <div className="text-black font-[500] text-[16px]">Evaluator: {step.evaluator}
                                    </div>
                                </div>

                                {step.description && (
                                    <p className="pl-8 text-black">{step.description}</p>
                                )}

                                {step.verifications && step.verifications.length > 0 && (
                                    <ul className="pl-8 mt-2 space-y-1">
                                        {step.verifications.map((v, idx) => (
                                            <li key={idx} className="flex items-center gap-2 text-black">
                                                {v.label}
                                                <Image
                                                    src={prefixBasePath(
                                                        v.passed ? "/green_tick.png" : "/red_x.png"
                                                    )}
                                                    alt={v.passed ? "Passed" : "Failed"}
                                                    width={20}
                                                    height={20}
                                                />
                                            </li>
                                        ))}
                                    </ul>
                                )}
                            </div>
                        );
                    })}
                </div>

                <div className="flex justify-start gap-4 w-full mt-8">
                    <button
                        onClick={onClose}
                        className="px-8 py-2 bg-gray-100 text-black rounded-[20px] hover:bg-gray-200 transition"
                    >
                        CLOSE
                    </button>
                </div>
            </div>
        </Modal>
    );
}
