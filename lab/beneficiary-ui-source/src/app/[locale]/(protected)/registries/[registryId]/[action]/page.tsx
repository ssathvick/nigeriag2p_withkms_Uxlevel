"use client";

import { useLocale } from "next-intl";
import Image from "next/image";
import { prefixBasePath } from "@/shared/utils/path";
import { AuthUtil } from "@/features/auth/components";
import { useParams, useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import { useAuth } from "@/context/GlobalContext";
import { Loading } from "@/components/shared";
import { Registry } from "@/features/registry/types";


const allRegistries: Registry[] = [
    {
        name: "Healthcare Registry",
        id: "12938475639",
        date: "15/08/2025",
        action: "Request for Update",
        description: "This registry serves as a comprehensive platform for tracking and managing all aspects of citizen healthcare programs. It maintains detailed records of medical history, immunizations, hospital visits, treatment plans, insurance coverage, and eligibility for healthcare benefits. The system ensures transparency and accountability by recording every update, application, and action taken within healthcare programs. Government agencies and healthcare providers can use this data to monitor public health trends, allocate resources effectively, and design initiatives that address community needs. Citizens can submit new applications for programs"
    },
    {
        name: "Employment Registry",
        id: "84756392013",
        date: "05/08/2025",
        action: "Request for Update",
        description: "The Employment Registry provides a centralized platform for managing citizen employment records and workforce participation. It tracks job applications, placements, unemployment benefits, vocational training participation, and professional certifications. This registry helps government and administrative agencies monitor labor market trends, identify skill gaps, plan workforce development programs, and ensure fair distribution of employment opportunities. Every update, application, and verification is logged to ensure accountability. Users can update personal employment information, submit applications for job assistance programs."
    },
    {
        name: "Housing Registry",
        id: "56473829102",
        date: "22/07/2025",
        action: "Request for Update",
        description: "This registry is dedicated to managing citizen housing information, including public housing allocations, rental assistance programs, housing subsidies, property ownership records, and eligibility verification. It allows government agencies to track occupancy, monitor housing demand, ensure fair distribution of housing benefits, and plan urban development projects. Citizens can update their housing information, submit applications for housing programs, and track approval status. Every action, change, or update in the registry is recorded to maintain transparency and accountability. The registry also provides comprehensive reporting."
    },
    {
        name: "Education Registry",
        id: "93847561029",
        date: "10/07/2025",
        action: "Request for Update",
        description: "The Education Registry provides a detailed and structured platform for tracking educational enrollment, academic performance, scholarship programs, training opportunities, and participation in educational initiatives. It ensures that every student's information, from primary school enrollment to higher education records, is accurately maintained. Government agencies, schools, and educational institutions can monitor student progress, allocate resources efficiently, and design policies to improve learning outcomes. Users can submit updates to their records, apply for scholarships or educational benefits, and track the status."
    },
    {
        name: "Pension Registry",
        id: "38475619283",
        date: "28/06/2025",
        action: "Request for Update",
        description: "The Pension Registry manages citizen retirement and pension-related records, including eligibility verification, contribution history, disbursement schedules, and beneficiary information. It ensures that retirees receive timely benefits and allows authorities to monitor compliance, detect discrepancies, and optimize resource allocation. Citizens can update their personal information, request adjustments to pension disbursements, and track payment schedules. Every application, record change, and action is logged to maintain accountability. The registry also provides analytical insights to support policymaking, reporting."
    },
    {
        name: "Social Services Registry",
        id: "19283746501",
        date: "12/06/2025",
        action: "Request for Update",
        description: "The Social Services Registry maintains records of citizen participation in welfare and assistance programs, including food aid, housing support, emergency relief, and other social benefits. It allows agencies to track applications, verify eligibility, monitor benefit distribution, and assess program effectiveness. Users can update their personal information, apply for assistance programs, and track the status of requests. Every update and action is recorded to ensure transparency and accountability. This registry supports data-driven policy decisions, reporting, and program planning, enabling social services."
    },
    {
        name: "Transport Registry",
        id: "91827364502",
        date: "03/06/2025",
        action: "Request for Update",
        description: "The Transport Registry tracks all citizen-related transportation services, including vehicle registrations, driving licenses, permits, public transport access, and road safety programs. It allows government authorities to monitor transport infrastructure usage, enforce compliance, allocate resources, and improve service delivery. Citizens can submit updates to their transport records, apply for permits, and track application progress. All updates, applications, and actions are logged for transparency and accountability. The registry also provides reporting and analytical capabilities, helping policymakers optimize."
    },
    {
        name: "Energy Registry",
        id: "56473829103",
        date: "25/05/2025",
        action: "Request for Update",
        description: "The Energy Registry provides a comprehensive system for tracking electricity, gas, and renewable energy services for citizens. It maintains detailed records of service subscriptions, usage patterns, billing, subsidies, and eligibility for energy assistance programs. Authorities can monitor consumption trends, manage energy distribution, and plan initiatives for sustainable energy use. Citizens can update their service information, apply for new programs, and track requests. Every update and action is logged to maintain transparency and accountability. The registry also provides data-driven insights to support energy policy."
    },
    {
        name: "Water Supply Registry",
        id: "84756392014",
        date: "15/05/2025",
        action: "Request for Update",
        description: "The Water Supply Registry manages citizen records related to water connections, usage, billing, and eligibility for subsidies or assistance programs. It enables authorities to monitor water consumption, plan infrastructure projects, manage resources, and ensure equitable distribution of services. Citizens can update their water supply records, request new connections, and track the progress of their applications. Every change and action is logged for accountability and transparency. The registry also supports reporting, analysis, and planning of water services, ensuring that programs are efficient, effective."
    },
    {
        name: "Telecom Registry",
        id: "29384756104",
        date: "02/05/2025",
        action: "Request for Update",
        description: "The Telecom Registry tracks all citizen-related telecommunications services, including phone subscriptions, internet connections, service providers, and eligibility for subsidized programs. It allows regulatory authorities to monitor service coverage, ensure compliance, allocate resources, and support digital inclusion initiatives. Citizens can update their telecom information, request new services, and track application status. All actions and updates are logged for transparency and accountability. The registry also provides analytical insights, enabling policymakers to plan initiatives."
    },
    {
        name: "Public Safety Registry",
        id: "38475619284",
        date: "28/04/2025",
        action: "Request for Update",
        description: "This registry includes detailed records of citizen interactions with public safety authorities, including police reports, emergency services, safety programs, and community policing initiatives. It allows authorities to monitor safety trends, allocate resources effectively, and ensure timely response to incidents. Citizens can request updates to their records, submit applications for safety programs, and track requests. Every update and action is logged for transparency and accountability. The system supports planning, reporting, and analysis of public safety programs, ensuring community protection."
    },
    {
        name: "Environment Registry",
        id: "93847561030",
        date: "18/04/2025",
        action: "Request for Update",
        description: "The Environment Registry tracks citizen participation in environmental programs, compliance with regulations, conservation initiatives, pollution monitoring, and sustainability projects. It allows agencies to monitor environmental trends, enforce regulations, and plan sustainable initiatives. Citizens can update their participation records, apply for environmental programs, and track progress. All updates and actions are logged to maintain transparency and accountability. The registry supports reporting, planning, and analytical insights, ensuring that environmental initiatives are effective."
    },
    {
        name: "Housing Welfare Registry",
        id: "12938475640",
        date: "10/04/2025",
        action: "Request for Update",
        description: "This registry monitors housing welfare programs, subsidies, and citizen eligibility for affordable housing schemes. It allows authorities to track allocations, verify eligibility, and monitor outcomes of welfare programs. Citizens can update their personal and housing information, submit applications for assistance, and track program status. All actions and updates are recorded for transparency and accountability. The registry also provides analytical insights for planning, reporting, and program evaluation, ensuring that housing assistance reaches intended populations efficiently."
    },
    {
        name: "Job Training Registry",
        id: "84756392015",
        date: "01/04/2025",
        action: "Request for Update",
        description: "The Job Training Registry keeps records of citizen participation in vocational training, skill development programs, apprenticeships, and employment readiness initiatives. It allows government agencies to monitor program effectiveness, track participant progress, and allocate resources efficiently. Users can update their training records, apply for new programs, and track progress. Every update and action is logged for accountability. The registry provides data-driven insights, supporting planning, reporting, and evaluation of training programs to enhance workforce capabilities and employability."
    },
    {
        name: "Childcare Registry",
        id: "56473829105",
        date: "22/03/2025",
        action: "Request for Update",
        description: "This registry manages citizen participation in childcare programs, early childhood education, and related support services. It tracks enrollments, eligibility, subsidies, and program outcomes. Authorities can monitor childcare availability, plan initiatives, and allocate resources effectively. Citizens can update personal and child information, apply for programs, and track requests. Every action is logged to ensure transparency and accountability. The registry also supports reporting, analysis, and planning for childcare services to ensure accessibility, quality, and equitable delivery."
    },
    {
        name: "Elderly Care Registry",
        id: "93847561031",
        date: "15/03/2025",
        action: "Request for Update",
        description: "The Elderly Care Registry tracks citizen participation in senior care programs, including healthcare, social support, pensions, and assisted living services. It allows authorities to monitor the well-being of elderly populations, allocate resources, and plan targeted interventions. Citizens can update personal information, request program support, and track their applications. All updates and actions are recorded to maintain transparency and accountability. The registry also provides analytical insights to support planning, reporting, and evaluation of elderly care programs, ensuring effective and timely delivery of services."
    }
];

export default function RegistryActionPage() {
    const lang = useLocale();
    const router = useRouter();
    const params = useParams();
    const registryId = params.registryId;
    const action = params.action;

    AuthUtil({ failedRedirectUrl: `/${lang}/login` });

    const { profile } = useAuth();
    const [registry, setRegistry] = useState<any>(null);
    const [name, setName] = useState("");
    const [userId, setUserId] = useState("");
    const [email, setEmail] = useState("");
    const [contactNumber, setContactNumber] = useState("");
    const [currentAddress, setCurrentAddress] = useState("");
    const [location, setLocation] = useState("");
    const [newAddress, setNewAddress] = useState("");
    const [uploadedFile, setUploadedFile] = useState<File | null>(null);

    const [registrationDate, setRegistrationDate] = useState("");
    const [registrationTime, setRegistrationTime] = useState("");
    const [workerRegistered, setWorkerRegistered] = useState("");
    const [otherBoardMember, setOtherBoardMember] = useState("");
    const [agree, setAgree] = useState("");

    useEffect(() => {
        if (profile) {
            setName(profile.name || "");
            setUserId(profile.provider_unique_id || "");
            setEmail(profile.email || "");
            setContactNumber(profile.phone_number || "");
            setCurrentAddress("#205, ABC Apartment,\nEFG Nagar Street, HIJK Road,\nBangalore, Karnataka - 500 001.");
            setLocation("Bangalore, Karnataka, India.");
        }
    }, [profile]);

    useEffect(() => {
        const selectedRegistry = allRegistries.find((r) => r.id === registryId) || null;
        setRegistry(selectedRegistry);
    }, [registryId]);

    const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setUploadedFile(e.target.files[0]);
        }
    };

    if (!registry) return <Loading title={"Registries"} height={"670px"} />;

    const isAddressChange = action === "address-change";
    const leftHeading = isAddressChange ? "Change Address" : "Social Welfare Registration";
    const rightHeading = isAddressChange ? "Personal Details" : "Registry Details";

    return (
        <div className="px-10 py-8 bg-white min-h-screen">
            <h1 className="text-[18px] font-[600] text-gray-800 mb-2">Registries</h1>

            <div className="flex flex-row gap-0 rounded-lg shadow-sm overflow-hidden border border-gray-200">
                <div className="w-[70%] bg-white p-8">
                    <h2 className="text-[20px] font-[600] text-[#ED7C22] mb-4">{leftHeading}</h2>

                    {isAddressChange ? (
                        <div className="flex flex-col gap-6">
                            <div>
                                <label className="block text-[14px] font-[400] text-gray-500 mb-2">Name</label>
                                <div className="text-[16px] font-[500] text-[#4A9EFF]">{name}</div>
                            </div>

                            <div className="flex gap-6">
                                <div className="flex-1">
                                    <label className="block text-[16px] font-[600] text-black mb-2">Current Address</label>
                                    <div className="border-2 border-dashed border-gray-300 rounded-md p-4 h-[120px]">
                                        <div className="text-[14px] text-black whitespace-pre-line">{currentAddress}</div>
                                    </div>
                                </div>

                                <div className="flex-1 flex flex-col">
                                    <label className="block text-[16px] font-[600] text-black mb-2">New Address</label>
                                    <div className="relative">
                                        <textarea
                                            placeholder="Enter new address"
                                            value={newAddress}
                                            onChange={(e) => setNewAddress(e.target.value)}
                                            className="w-full h-[120px] bg-gray-100 rounded-md px-4 pt-3 pb-3 text-[14px] text-black focus:outline-none focus:ring-2 focus:ring-gray-300 resize-none"
                                        />
                                        <div className="absolute right-4 top-4 pointer-events-none">
                                            <Image src={prefixBasePath("/arrow_02.png")} alt="Dropdown" width={16} height={16} />
                                        </div>
                                    </div>

                                    {/* Upload section aligned under New Address */}
                                    <div className="mt-4">
                                        <label className="block text-[16px] font-[600] text-black mb-2">Upload Address Proof</label>
                                        <div className="relative">
                                            <input
                                                type="file"
                                                id="fileUpload"
                                                onChange={handleFileUpload}
                                                className="hidden"
                                                accept=".pdf,.jpg,.jpeg,.png"
                                            />
                                            <label
                                                htmlFor="fileUpload"
                                                className="flex items-center justify-between w-full bg-gray-100 rounded-md px-4 py-3 text-[14px] text-gray-400 cursor-pointer hover:bg-gray-200 transition"
                                            >
                                                <span>{uploadedFile ? uploadedFile.name : "Upload file"}</span>
                                                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                                                    <path d="M10 14V6M10 6L7 9M10 6L13 9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                                    <path d="M4 14V16C4 16.5304 4.21071 17.0391 4.58579 17.4142C4.96086 17.7893 5.46957 18 6 18H14C14.5304 18 15.0391 17.7893 15.4142 17.4142C15.7893 17.0391 16 16.5304 16 16V14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                                </svg>
                                            </label>
                                        </div>

                                        {uploadedFile && (
                                            <div className="mt-2">
                                                <label className="block text-[16px] font-[600] text-black mb-2">Uploaded File</label>
                                                <div className="flex items-center gap-3">
                                                    <div className="w-12 h-12 bg-red-100 rounded flex items-center justify-center">
                                                        <span className="text-red-600 text-xs font-bold">PDF</span>
                                                    </div>
                                                    <span className="text-[14px] text-gray-600">{uploadedFile.name}</span>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>

                    ) : (
                        <div className="flex flex-col gap-4">
                            <div className="flex-1 pr-2 w-1/2">
                                <label className="block text-[16px] font-[500] text-black mb-1">Registry Name</label>
                                <input
                                    type="text"
                                    className="w-full bg-gray-100 rounded-md px-4 py-2 text-[16px] text-black/50 focus:outline-none"
                                    value={registry.name}
                                    readOnly
                                />
                            </div>

                            <div className="flex gap-4">
                                <div className="flex-1">
                                    <label className="block text-[16px] font-[500] text-black mb-1">Name</label>
                                    <input
                                        type="text"
                                        className="w-full bg-gray-100 rounded-md px-4 py-2 text-[16px] text-black/50 focus:outline-none"
                                        value={name}
                                        onChange={(e) => setName(e.target.value)}
                                    />
                                </div>
                                <div className="flex-1">
                                    <label className="block text-[16px] font-[500] text-black mb-1">ID</label>
                                    <input
                                        type="text"
                                        className="w-full bg-gray-100 rounded-md px-4 py-2 text-[16px] text-black/50 focus:outline-none"
                                        value={userId}
                                        onChange={(e) => setUserId(e.target.value)}
                                    />
                                </div>
                            </div>

                            <div className="flex gap-4">
                                <div className="flex-1">
                                    <label className="block text-[16px] font-[500] text-black mb-1">Whether Worker is Registered</label>
                                    <div className="relative">
                                        <select
                                            value={workerRegistered}
                                            onChange={(e) => setWorkerRegistered(e.target.value)}
                                            className="appearance-none w-full bg-gray-100 rounded-md px-4 py-2 text-[16px] text-black/50 cursor-pointer border-0 focus:outline-none focus:ring-0"
                                        >
                                            <option value="">Select</option>
                                            <option value="yes">Yes</option>
                                            <option value="no">No</option>
                                        </select>
                                        <div className="pointer-events-none absolute right-5 top-1/2 transform -translate-y-1/2">
                                            <Image src={prefixBasePath("/arrow_02.png")} alt="Dropdown arrow" width={20} height={20} />
                                        </div>
                                    </div>
                                </div>

                                <div className="flex-1">
                                    <label className="block text-[16px] font-[500] text-black mb-1">Member of other State Welfare Board?</label>
                                    <div className="relative">
                                        <select
                                            value={otherBoardMember}
                                            onChange={(e) => setOtherBoardMember(e.target.value)}
                                            className="appearance-none w-full bg-gray-100 rounded-md px-4 py-2 text-[16px] text-black/50 cursor-pointer border-0 focus:outline-none focus:ring-0"
                                        >
                                            <option value="">Select</option>
                                            <option value="yes">Yes</option>
                                            <option value="no">No</option>
                                        </select>
                                        <div className="pointer-events-none absolute right-5 top-1/2 transform -translate-y-1/2">
                                            <Image src={prefixBasePath("/arrow_02.png")} alt="Dropdown arrow" width={20} height={20} />
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="flex gap-4">
                                <div className="flex-1">
                                    <label className="block text-[16px] font-[500] text-black mb-1">Registration Date</label>
                                    <input
                                        type="date"
                                        value={registrationDate}
                                        onChange={(e) => setRegistrationDate(e.target.value)}
                                        className="w-full bg-gray-100 rounded-md px-4 py-2 text-[16px] text-black/50 focus:outline-none"
                                    />
                                </div>
                                <div className="flex-1">
                                    <label className="block text-[16px] font-[500] text-black mb-1">Time</label>
                                    <input
                                        type="time"
                                        value={registrationTime}
                                        onChange={(e) => setRegistrationTime(e.target.value)}
                                        className="w-full bg-gray-100 rounded-md px-4 py-2 text-[16px] text-black/50 focus:outline-none"
                                    />
                                </div>
                            </div>

                            <div className="flex gap-4">
                                <div className="flex-1">
                                    <label className="block text-[16px] font-[500] text-black mb-1">Do you agree with the terms?</label>
                                    <div className="flex gap-4">
                                        <label className="flex items-center gap-2 text-black">
                                            <input type="radio" name="agree" value="yes" checked={agree === "yes"} onChange={() => setAgree("yes")} />
                                            Yes
                                        </label>
                                        <label className="flex items-center gap-2 text-black">
                                            <input type="radio" name="agree" value="no" checked={agree === "no"} onChange={() => setAgree("no")} />
                                            No
                                        </label>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                <div className="w-[30%] bg-gray-100 p-8 flex flex-col gap-4 justify-between">
                    <div>
                        <h2 className="text-[20px] font-[600] text-[#ED7C22] mb-6">{rightHeading}</h2>

                        {isAddressChange ? (
                            <>
                                <div className="mb-4">
                                    <label className="block text-[14px] font-[400] text-gray-500 mb-1">Name</label>
                                    <div className="text-[16px] text-black font-[600]">{name}</div>
                                </div>

                                <div className="mb-4">
                                    <label className="block text-[14px] font-[400] text-gray-500 mb-1">ID</label>
                                    <div className="text-[16px] text-black font-[600]">{userId}</div>
                                </div>

                                <div className="mb-4">
                                    <label className="block text-[14px] font-[400] text-gray-500 mb-1">Email ID</label>
                                    <div className="text-[16px] text-black font-[600]">{email}</div>
                                </div>

                                <div className="mb-4">
                                    <label className="block text-[14px] font-[400] text-gray-500 mb-1">Contact Number</label>
                                    <div className="text-[16px] text-black font-[600]">{contactNumber}</div>
                                </div>

                                <div className="mb-4">
                                    <label className="block text-[14px] font-[400] text-gray-500 mb-1">Address</label>
                                    <div className="text-[16px] text-black font-[600] whitespace-pre-line">{currentAddress}</div>
                                </div>

                                <div>
                                    <label className="block text-[14px] font-[400] text-gray-500 mb-1">Location</label>
                                    <div className="text-[16px] text-black font-[600]">{location}</div>
                                </div>
                            </>
                        ) : (
                            <>
                                <div className="mb-4">
                                    <label className="block text-[16px] font-[500] text-black/50 mb-1">Registry Name</label>
                                    <div className="text-[16px] text-black font-[500]">{registry.name}</div>
                                </div>

                                <div className="mb-4">
                                    <label className="block text-[16px] font-[500] text-black/50 mb-1">Date</label>
                                    <div className="text-[16px] text-black font-[500]">{registry.date}</div>
                                </div>

                                <div>
                                    <label className="block text-[16px] font-[500] text-black mb-1">Description</label>
                                    <p className="text-[16px] text-black font-[500] leading-relaxed">{registry.description}</p>
                                </div>
                            </>
                        )}
                    </div>

                    <div className="flex gap-4 mt-4">
                        <button
                            onClick={() => router.back()}
                            className="px-6 py-2 bg-gray-200 text-gray-800 font-[500] rounded-[20px] w-full hover:bg-gray-300 transition"
                        >
                            BACK
                        </button>
                        <button className="px-6 py-2 bg-black text-white font-[500] rounded-[20px] w-full hover:bg-gray-800 transition">
                            SUBMIT
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
