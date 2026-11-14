"use client";
import React from "react"

import { Benefit } from "@/features/disbursement/types";
import Modal from "@/components/ui/Modal";

interface TransferHistoryProps {
    benefit: Benefit;
    onClose: () => void;
}

export default function TransferHistory({ benefit, onClose }: TransferHistoryProps) {
    const transferHistory = [
        { transferId: "2389009856", receivedFund: 300.0, refNum: "3456677800", dateApproved: "25-06-2025", dateReceived: "27-06-2025" },
        { transferId: "2389009857", receivedFund: 500.0, refNum: "3456677801", dateApproved: "01-07-2025", dateReceived: "03-07-2025" },
        { transferId: "2389009858", receivedFund: 250.0, refNum: "3456677802", dateApproved: "05-07-2025", dateReceived: "07-07-2025" },
        { transferId: "2389009859", receivedFund: 400.0, refNum: "3456677803", dateApproved: "10-07-2025", dateReceived: "12-07-2025" },
        { transferId: "2389009860", receivedFund: 350.0, refNum: "3456677804", dateApproved: "15-07-2025", dateReceived: "17-07-2025" },
        { transferId: "2389009861", receivedFund: 450.0, refNum: "3456677805", dateApproved: "20-07-2025", dateReceived: "22-07-2025" },
        { transferId: "2389009862", receivedFund: 600.0, refNum: "3456677806", dateApproved: "25-07-2025", dateReceived: "27-07-2025" },
        { transferId: "2389009863", receivedFund: 700.0, refNum: "3456677807", dateApproved: "30-07-2025", dateReceived: "01-08-2025" },
    ];

    return (
        <Modal
            title={
                <span>
                    <span className="text-[#ED7C22] text-2xl">Openg2p Safety Program</span>{" "}
                    <span className="text-[#3399FF] text-lg">Transfer History</span>
                </span>
            }
            onClose={onClose}
            width="900px"
            height="580px"
            sidebarWidth="9%"
            paddingXClass="px-12"
        >

            <div className="flex-1 overflow-y-auto">
                <table className="w-full text-left border-collapse">
                    <thead className="text-black bg-gray-100">
                        <tr>
                            <th className="text-sm">
                                <div className="pl-12 py-4">Transfer ID</div>
                            </th>
                            <th className="text-sm">
                                <div className="pl-12 py-4">Received Fund</div>
                            </th>
                            <th className="text-sm">
                                <div className="pl-12 py-4">Reference Number</div>
                            </th>
                            <th className="text-sm">
                                <div className="pl-12 py-4">Date of Approval</div>
                            </th>
                            <th className="text-sm">
                                <div className="px-12 py-4">Date of Receipt</div>
                            </th>
                        </tr>
                    </thead>
                    <tbody className="divide-y">
                        {transferHistory.map((transfer, index) => (
                            <tr
                                key={index}
                                className={`transition-colors duration-150 ${index % 2 === 0 ? "bg-white" : "bg-gray-100"
                                    }`}
                            >
                                <td className="text-sm text-gray-900">
                                    <div className="pl-12 py-2">{transfer.transferId}</div>
                                </td>
                                <td className="text-sm text-black font-semibold">
                                    <div className="pl-12 py-2">
                                        <span className="text-[#00B765] font-bold">{transfer.receivedFund.toFixed(2)}</span> $
                                    </div>
                                </td>
                                <td className="text-sm text-gray-900">
                                    <div className="pl-12 py-2">{transfer.refNum}</div>
                                </td>
                                <td className="text-sm text-gray-900">
                                    <div className="pl-12 py-2">{transfer.dateApproved}</div>
                                </td>
                                <td className="text-sm text-gray-900">
                                    <div className="px-12 py-2">{transfer.dateReceived}</div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>


            <div className="flex justify-start gap-4 w-full my-10 px-12">
                <button
                    onClick={onClose}
                    className="px-8 py-2 bg-black text-white text-xl rounded-full"
                >
                    BACK
                </button>
            </div>
        </Modal>
    );
};
