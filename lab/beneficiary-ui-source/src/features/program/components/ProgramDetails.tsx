"use client";

import { Program } from "@/features/program/types";
import Modal from "@/components/ui/Modal";
import { getColorForBenefit } from "@/features/program/utils"


interface ProgramDetailsProps {
    program: Program;
    onClose: () => void;
}

export default function ProgramDetails({ program, onClose }: ProgramDetailsProps) {
    return (
        <Modal
            title={<span className="text-[#ED7C22] text-[24px]">Program Details</span>}
            onClose={onClose}
            width="900px"
            height="650px"
            sidebarWidth="25%"
            sidebarImage="/program_details.png"
        >
            <div className="space-y-5 px-10">
                <div>
                    <label className="block text-[16px] text-black/50 font-[600] mb-1">Program Name</label>
                    <div className="text-[16px] text-black font-[600]">{program.program_mnemonic}</div>
                </div>

                <div className="flex gap-8">
                    <div>
                        <label className="block text-[16px] text-black/50 font-[600] mb-1">Date</label>
                        <div className="text-[16px] text-black font-[600]">{program.enrolment_date}</div>
                    </div>
                    <div>
                        <label className="block text-[16px] text-black/50 font-[600] mb-1">Application ID</label>
                        <div className="text-[16px] text-black font-[600]">{program.id}</div>
                    </div>
                </div>

                <div>
                    <label className="block text-sm font-bold text-black mb-1">Benefits</label>
                    <div className="flex flex-wrap gap-2">
                        {program.benefit_codes.map((b) => {
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
                </div>

                <div>
                    <p className="text-[16px] text-black font-normal leading-relaxed">
                        {program.program_description}
                    </p>
                </div>
            </div>
            <div className="flex justify-start gap-4 w-full my-8 px-10">
                <button
                    onClick={onClose}
                    className="px-8 py-2 bg-gray-100 text-black rounded-[20px]"
                >
                    CLOSE
                </button>
            </div>
        </Modal>
    );
}
