"use client";

import Image from "next/image";

import Modal from "@/components/ui/Modal";
import { prefixBasePath } from "@/shared/utils/path";

export interface Agent {
    name: string;
    address: string;
}

export interface ReceivedBenefit {
    programName: string;
    benefitCode: string;
    quantity: string;
    dateReceived: string;
    agent: Agent;
    deliveryDateTime: string;
    address: string;
    mapImageUrl: string;
    evidenceImages: string[];
    biometricVerified: boolean;
    verificationType: string;
}

interface DeliveryDetailsProps {
    benefit: ReceivedBenefit;
    onClose: () => void;
}

export default function DeliveryDetails({ benefit, onClose }: DeliveryDetailsProps) {
    return (
        <Modal
            title={<span className="text-[#ED7C22] text-[24px]">Delivery Details</span>}
            onClose={onClose}
            width="900px"
            height="700px"
            sidebarWidth="25%"
            sidebarImage="/delivery_details.png"
        >
            <div className="space-y-5 overflow-y-auto">
                <div className="bg-gray-100 px-10 py-1">
                    <label className="block text-[16px] text-black/50 font-[600] mb-1">
                        Program Name
                    </label>
                    <div className="text-[16px] text-black font-[600]">
                        {benefit.programName}
                    </div>
                </div>

                <div className="px-10">
                    <label className="block text-[16px] text-black/50 font-[600] mb-1">
                        Agent Details
                    </label>
                    <div className="text-[16px] text-black font-[600]">
                        {benefit.agent.name} — {benefit.agent.address}
                    </div>
                </div>

                <div className="bg-gray-100 px-10 py-1">
                    <label className="block text-[16px] text-black/50 font-[600] mb-1">
                        Delivery Date & Time
                    </label>
                    <div className="text-[16px] text-black font-[600]">
                        {benefit.deliveryDateTime}
                    </div>
                </div>

                <div className="flex gap-6 px-10">
                    <div className="flex-1">
                        <label className="block text-[16px] text-black/50 font-[600] mb-1">
                            Address
                        </label>
                        <div className="text-[16px] text-black font-[600]">
                            {benefit.address}
                        </div>
                    </div>
                    <div className="flex-1">
                        <Image
                            src={prefixBasePath(benefit.mapImageUrl)}
                            alt="Map"
                            width={320}
                            height={120}
                            className="rounded-md border"
                        />
                    </div>
                </div>

                <div className="flex items-start justify-between gap-6 bg-gray-100 px-10 py-1">
                    <label className="block text-[16px] text-black/50 font-[600] shrink-0">
                        Evidence Pictures
                    </label>

                    <div className="flex flex-wrap justify-end gap-3 flex-1">
                        {benefit.evidenceImages.map((img, index) => (
                            <Image
                                key={index}
                                src={prefixBasePath(img)}
                                alt={`Evidence ${index + 1}`}
                                width={100}
                                height={80}
                                className="rounded-md object-cover border"
                            />
                        ))}
                    </div>
                </div>

                <div className="flex items-center justify-between gap-6 px-10">
                    <div className="flex-1 flex flex-col gap-2">
                        <div>
                            <label className="block text-[16px] text-black/50 font-[600]">
                                Biometric Verification
                            </label>
                        </div>

                        <div className="flex items-center gap-4">
                            <span className="text-[16px] text-black font-[600]">
                                Verified or Not
                            </span>
                            <label className="flex text-black items-center gap-1">
                                <input
                                    type="radio"
                                    checked={benefit.biometricVerified}
                                    readOnly
                                />
                                Yes
                            </label>
                            <label className="flex text-black items-center gap-1">
                                <input
                                    type="radio"
                                    checked={!benefit.biometricVerified}
                                    readOnly
                                />
                                No
                            </label>
                        </div>
                    </div>


                    <div className="flex-1 flex items-center justify-between">
                        <div>
                            <label className="block text-[16px] text-black/50 font-[600] mb-1">
                                Verification Type
                            </label>
                            <span className="text-[16px] text-black font-[600]">
                                {benefit.verificationType}
                            </span>
                        </div>
                        {benefit.verificationType.toLowerCase() === "fingerprint" && (
                            <Image
                                src={prefixBasePath("/fingerprint.png")}
                                alt="Fingerprint"
                                width={60}
                                height={60}
                            />
                        )}
                    </div>
                </div>
            </div>

            <div className="flex justify-start gap-4 w-full my-4 px-10">
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
