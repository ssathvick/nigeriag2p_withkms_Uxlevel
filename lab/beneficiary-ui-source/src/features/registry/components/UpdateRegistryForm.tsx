"use client";
import { useState } from "react";

import { Registry } from "@/features/registry/types/registry";
import Modal from "@/components/ui/Modal";

interface UpdateRegistryFormProps {
    registry: Registry;
    onClose: () => void;
}

export default function UpdateRegistryForm({ registry, onClose }: UpdateRegistryFormProps) {
    const [yourName, setYourName] = useState("");
    const [yourEmail, setYourEmail] = useState("");

    const handleSave = () => {
        console.log("Updated registry:", {
            registryName: registry.name,
            registryId: registry.id,
            yourName,
            yourEmail,
        });
        onClose();
    };

    return (
        <Modal
            title={<span className="text-[#ED7C22] text-2xl">Update Registry</span>}
            onClose={onClose}
            width="800px"
            height="580px"
            sidebarWidth="25%"
            sidebarImage="/apply_program.png"
        >
            <div className="space-y-9 px-10">
                <div>
                    <label className="block text-sm font-bold text-black">Program Name</label>
                    <input
                        type="text"
                        value={registry.name}
                        disabled
                        className="mt-1 block w-full text-black rounded-md shadow-sm bg-gray-100 py-2 px-4"
                    />
                </div>
                <div>
                    <label className="block text-sm font-bold text-black">Registry ID</label>
                    <input
                        type="text"
                        value={registry.id}
                        disabled
                        className="mt-1 block w-full text-black rounded-md shadow-sm bg-gray-100 py-2 px-4"
                    />
                </div>
                <div>
                    <label className="block text-sm font-bold text-black">Your Name</label>
                    <input
                        type="text"
                        value={yourName}
                        onChange={(e) => setYourName(e.target.value)}
                        className="mt-1 block w-full text-black rounded-md shadow-sm bg-gray-100 py-2 px-4 focus:outline-none"
                    />
                </div>
                <div>
                    <label className="block text-sm font-bold text-black">Your Email ID</label>
                    <input
                        type="email"
                        value={yourEmail}
                        onChange={(e) => setYourEmail(e.target.value)}
                        className="mt-1 block w-full text-black rounded-md shadow-sm bg-gray-100 py-2 px-4 focus:outline-none"
                    />
                </div>
            </div>

            <div className="flex justify-start gap-4 w-full my-10 px-10">
                <button
                    onClick={onClose}
                    className="px-8 py-2 bg-gray-100 text-black rounded-[20px]"
                >
                    CANCEL
                </button>
                <button
                    className="px-8 py-2 bg-black text-white rounded-[20px]"
                >
                    SAVE
                </button>
            </div>
        </Modal>
    );
}
