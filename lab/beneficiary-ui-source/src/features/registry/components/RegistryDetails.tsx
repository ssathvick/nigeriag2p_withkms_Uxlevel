"use client";

import Modal from "@/components/ui/Modal";
import { Registry } from "@/features/registry/types";

interface RegistryDetailsProps {
    registry: Registry;
    onClose: () => void;
}

export default function RegistryDetails({ registry, onClose }: RegistryDetailsProps) {
    return (
        <Modal
            title={<span className="text-[#ED7C22] text-[24px]">Registry Details</span>}
            onClose={onClose}
            width="900px"
            height="700px"
            sidebarWidth="25%"
            sidebarImage="/registry_details.png"
        >
            <div className="space-y-5 px-10">
                <div>
                    <label className="block text-[16px] text-black/50 font-[600] mb-1">Registry Name</label>
                    <div className="text-[16px] text-black font-[600]">{registry.name}</div>
                </div>

                <div className="flex gap-8">
                    <div>
                        <label className="block text-[16px] text-black/50 font-[600] mb-1">
                            Date
                        </label>
                        <div className="text-[16px] text-black font-[600]">{registry.date}</div>
                    </div>
                    <div>
                        <label className="block text-[16px] text-black/50 font-[600] mb-1">
                            Registry ID
                        </label>
                        <div className="text-[16px] text-black font-[600]">{registry.id}</div>
                    </div>
                </div>

                {registry.description && (
                    <div>
                        <label className="block text-sm font-bold text-black mb-1">Description</label>
                        <p className="text-[16px] text-black font-normal leading-relaxed">
                            {registry.description}
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
