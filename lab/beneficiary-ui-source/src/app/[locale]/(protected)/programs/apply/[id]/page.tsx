"use client";

import { useLocale } from "next-intl";
import Image from "next/image";
import { prefixBasePath } from "@/shared/utils/path";

import { AuthUtil } from "@/features/auth/components";
import { useParams, useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import { useAuth } from "@/context/GlobalContext";
import { Program } from "@/features/program/types/program";
import { Loading } from "@/components/shared";

const allPrograms: Program[] = [
    {
        id: 1,
        program_mnemonic: "Adult Literacy Drive",
        program_description: "The Adult Literacy Drive aims to provide educational support and learning resources to adults across the country.",
        am_i_enrolled: true,
        enrolment_date: "2025-09-01 10:30 AM",
        benefit_codes: [
            {
                id: 1,
                benefit_code_mnemonic: "Books",
                benefit_type: "Learning Material",
                benefit_code_description: "Provides learning books for literacy.",
                benefit_code_max_quantity: 10
            },
            {
                id: 2,
                benefit_code_mnemonic: "Classes",
                benefit_type: "Education Service",
                benefit_code_description: "Free literacy classes.",
                benefit_code_max_quantity: 20
            }
        ]
    },
    {
        id: 2,
        program_mnemonic: "School Supplies Initiative",
        program_description: "Provides essential educational materials to children in need.",
        am_i_enrolled: false,
        enrolment_date: "2025-08-15 09:10 AM",
        benefit_codes: [
            {
                id: 3,
                benefit_code_mnemonic: "Books",
                benefit_type: "Learning Material",
                benefit_code_description: "School book assistance.",
                benefit_code_max_quantity: 5
            },
            {
                id: 4,
                benefit_code_mnemonic: "Uniforms",
                benefit_type: "Apparel",
                benefit_code_description: "School uniform support.",
                benefit_code_max_quantity: 2
            }
        ]
    },
    {
        id: 3,
        program_mnemonic: "Social Registry Upgrade",
        program_description: "Improves the management of social welfare records.",
        am_i_enrolled: true,
        enrolment_date: "2025-08-10 02:15 PM",
        benefit_codes: [
            {
                id: 5,
                benefit_code_mnemonic: "Information Access",
                benefit_type: "Digital Service",
                benefit_code_description: "Access to updated digital records.",
                benefit_code_max_quantity: 1
            }
        ]
    },
    {
        id: 4,
        program_mnemonic: "Income Tax Assistance",
        program_description: "Assists individuals and small businesses with tax compliance.",
        am_i_enrolled: true,
        enrolment_date: "2025-08-20 11:45 AM",
        benefit_codes: [
            {
                id: 6,
                benefit_code_mnemonic: "Money",
                benefit_type: "Financial Help",
                benefit_code_description: "Rebate or subsidy.",
                benefit_code_max_quantity: 1
            },
            {
                id: 7,
                benefit_code_mnemonic: "Guidance",
                benefit_type: "Advisory",
                benefit_code_description: "Professional tax advisory guidance.",
                benefit_code_max_quantity: 5
            }
        ]
    },
    {
        id: 5,
        program_mnemonic: "Caste Certificate Facilitation",
        program_description: "Assists in obtaining caste certificates.",
        am_i_enrolled: true,
        enrolment_date: "2025-07-25 03:30 PM",
        benefit_codes: [
            {
                id: 8,
                benefit_code_mnemonic: "Documentation",
                benefit_type: "Support Service",
                benefit_code_description: "Help with application paperwork.",
                benefit_code_max_quantity: 1
            }
        ]
    },
    {
        id: 6,
        program_mnemonic: "Electricity Subsidy Program",
        program_description: "Provides financial assistance for electricity bills.",
        am_i_enrolled: true,
        enrolment_date: "2025-07-15 04:10 PM",
        benefit_codes: [
            {
                id: 9,
                benefit_code_mnemonic: "Money",
                benefit_type: "Financial Subsidy",
                benefit_code_description: "Subsidy for electricity bill.",
                benefit_code_max_quantity: 12
            },
            {
                id: 10,
                benefit_code_mnemonic: "Support",
                benefit_type: "Assistance",
                benefit_code_description: "Help with electricity bill issues.",
                benefit_code_max_quantity: 5
            }
        ]
    },
    {
        id: 7,
        program_mnemonic: "Voter Registry Update",
        program_description: "Maintains accurate and current electoral rolls.",
        am_i_enrolled: false,
        enrolment_date: "2025-09-02 11:00 AM",
        benefit_codes: [
            {
                id: 11,
                benefit_code_mnemonic: "Verification",
                benefit_type: "Validation Service",
                benefit_code_description: "Voter identity verification service.",
                benefit_code_max_quantity: 1
            }
        ]
    },
    {
        id: 8,
        program_mnemonic: "Unemployment Registry Support",
        program_description: "Provides assistance and guidance to job seekers.",
        am_i_enrolled: false,
        enrolment_date: "2025-08-18 01:20 PM",
        benefit_codes: [
            {
                id: 12,
                benefit_code_mnemonic: "Information Access",
                benefit_type: "Digital Service",
                benefit_code_description: "Access to unemployment registry.",
                benefit_code_max_quantity: 1
            },
            {
                id: 13,
                benefit_code_mnemonic: "Guidance",
                benefit_type: "Advisory",
                benefit_code_description: "Professional job counseling.",
                benefit_code_max_quantity: 10
            }
        ]
    },
    {
        id: 9,
        program_mnemonic: "Disability Registry Program",
        program_description: "Provides accurate records and assistance for persons with disabilities.",
        am_i_enrolled: false,
        enrolment_date: "2025-08-28 03:15 PM",
        benefit_codes: [
            {
                id: 14,
                benefit_code_mnemonic: "Documentation",
                benefit_type: "Support Service",
                benefit_code_description: "Certification assistance.",
                benefit_code_max_quantity: 1
            },
            {
                id: 15,
                benefit_code_mnemonic: "Support",
                benefit_type: "Aid Service",
                benefit_code_description: "Special support programs.",
                benefit_code_max_quantity: 5
            }
        ]
    },
    {
        id: 10,
        program_mnemonic: "Food Security Program",
        program_description: "Ensures access to nutritious food for low-income families.",
        am_i_enrolled: true,
        enrolment_date: "2025-09-03 09:00 AM",
        benefit_codes: [
            {
                id: 16,
                benefit_code_mnemonic: "Food Supplies",
                benefit_type: "Material Benefit",
                benefit_code_description: "Monthly food supply kit.",
                benefit_code_max_quantity: 12
            },
            {
                id: 17,
                benefit_code_mnemonic: "Nutrition",
                benefit_type: "Health Service",
                benefit_code_description: "Nutritional consultation.",
                benefit_code_max_quantity: 4
            }
        ]
    },
    {
        id: 11,
        program_mnemonic: "Water Access Improvement",
        program_description: "Provides clean and safe drinking water access.",
        am_i_enrolled: false,
        enrolment_date: "2025-08-22 10:30 AM",
        benefit_codes: [
            {
                id: 18,
                benefit_code_mnemonic: "Clean Water",
                benefit_type: "Essential Resource",
                benefit_code_description: "Free purified water.",
                benefit_code_max_quantity: 30
            },
            {
                id: 19,
                benefit_code_mnemonic: "Infrastructure",
                benefit_type: "Support Installation",
                benefit_code_description: "Water system installation.",
                benefit_code_max_quantity: 1
            }
        ]
    },
    {
        id: 12,
        program_mnemonic: "Healthcare Outreach",
        program_description: "Provides medical services in underserved areas.",
        am_i_enrolled: false,
        enrolment_date: "2025-08-30 11:15 AM",
        benefit_codes: [
            {
                id: 20,
                benefit_code_mnemonic: "Medical Checkups",
                benefit_type: "Health Service",
                benefit_code_description: "Free medical checkups.",
                benefit_code_max_quantity: 4
            },
            {
                id: 21,
                benefit_code_mnemonic: "Medicines",
                benefit_type: "Health Material",
                benefit_code_description: "Free basic medicines.",
                benefit_code_max_quantity: 6
            }
        ]
    },
    {
        id: 13,
        program_mnemonic: "Women Empowerment Workshops",
        program_description: "Provides training and development for women.",
        am_i_enrolled: true,
        enrolment_date: "2025-09-05 02:00 PM",
        benefit_codes: [
            {
                id: 22,
                benefit_code_mnemonic: "Training",
                benefit_type: "Skill Development",
                benefit_code_description: "Career training workshops.",
                benefit_code_max_quantity: 10
            },
            {
                id: 23,
                benefit_code_mnemonic: "Skills Development",
                benefit_type: "Learning",
                benefit_code_description: "Skill-building sessions.",
                benefit_code_max_quantity: 10
            }
        ]
    },
    {
        id: 14,
        program_mnemonic: "Digital Literacy Campaign",
        program_description: "Improves computer and digital skills.",
        am_i_enrolled: false,
        enrolment_date: "2025-09-06 09:45 AM",
        benefit_codes: [
            {
                id: 24,
                benefit_code_mnemonic: "Training",
                benefit_type: "Skill Development",
                benefit_code_description: "Computer training.",
                benefit_code_max_quantity: 15
            },
            {
                id: 25,
                benefit_code_mnemonic: "Devices",
                benefit_type: "Material",
                benefit_code_description: "Laptop or tablet loaner.",
                benefit_code_max_quantity: 1
            }
        ]
    },
    {
        id: 15,
        program_mnemonic: "Environmental Awareness Program",
        program_description: "Educates communities on environmental sustainability.",
        am_i_enrolled: false,
        enrolment_date: "2025-09-07 03:30 PM",
        benefit_codes: [
            {
                id: 26,
                benefit_code_mnemonic: "Workshops",
                benefit_type: "Training",
                benefit_code_description: "Environment workshops.",
                benefit_code_max_quantity: 5
            },
            {
                id: 27,
                benefit_code_mnemonic: "Community Engagement",
                benefit_type: "Social Service",
                benefit_code_description: "Environment projects.",
                benefit_code_max_quantity: 3
            }
        ]
    },
    {
        id: 16,
        program_mnemonic: "Skill Development Initiative",
        program_description: "Provides vocational and professional skills training.",
        am_i_enrolled: true,
        enrolment_date: "2025-09-08 10:00 AM",
        benefit_codes: [
            {
                id: 28,
                benefit_code_mnemonic: "Training",
                benefit_type: "Skill Development",
                benefit_code_description: "Vocational skill classes.",
                benefit_code_max_quantity: 8
            },
            {
                id: 29,
                benefit_code_mnemonic: "Certification",
                benefit_type: "Accreditation",
                benefit_code_description: "Skill assessment and certification.",
                benefit_code_max_quantity: 1
            }
        ]
    }
];



export default function ApplyProgramPage() {
    const lang = useLocale();
    const router = useRouter();
    const params = useParams();
    const programId = params.id;

    AuthUtil({ failedRedirectUrl: `/${lang}/login` });


    const [program, setProgram] = useState<Program | null>(null);
    const { profile } = useAuth();
    const [name, setName] = useState("");
    const [userId, setUserId] = useState("");

    useEffect(() => {
        if (profile) {
            setName(profile.name || "");
            setUserId(profile.provider_unique_id || "");
        }
    }, [profile]);

    useEffect(() => {
        const selectedProgram = allPrograms.find(p => p.id === Number(programId)) || null;
        setProgram(selectedProgram);
    }, [programId]);

    if (!program) return <Loading title={"Program Application"} height={"670px"} />

    return (
        <div className="px-10 py-8 bg-white min-h-screen">
            <h1 className="text-[18px] font-[600] text-gray-800 mb-2">Program Application</h1>

            <div className="flex flex-row gap-0 rounded-lg shadow-sm overflow-hidden border border-gray-200">
                <div className="w-[70%] bg-white p-8">
                    <h2 className="text-[20px] font-[600] text-[#ED7C22] mb-4">
                        Program Application Form
                    </h2>

                    <div className="flex flex-col gap-4">
                        <div className="flex-1 pr-2 w-1/2">
                            <label className="block text-[16px] font-[500] text-black mb-1">
                                Program Name
                            </label>
                            <input
                                type="text"
                                className="w-full bg-gray-100 rounded-md px-4 py-2 text-[16px] text-black/50 focus:outline-none"
                                value={program.program_mnemonic}
                                readOnly
                            />
                        </div>

                        <div className="flex gap-4">
                            <div className="flex-1">
                                <label className="block text-[16px] font-[500] text-black mb-1">
                                    Name
                                </label>
                                <input
                                    type="text"
                                    className="w-full bg-gray-100 rounded-md px-4 py-2 text-[16px] text-black/50 focus:outline-none"
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                />
                            </div>
                            <div className="flex-1">
                                <label className="block text-[16px] font-[500] text-black mb-1">
                                    ID
                                </label>
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
                                <label className="block text-[16px] font-[500] text-black mb-1">
                                    Whether Worker is Registered
                                </label>
                                <div className="relative">
                                    <select
                                        className="appearance-none w-full bg-gray-100 rounded-md px-4 py-2 text-[16px] text-black/50 cursor-pointer border-0 focus:outline-none focus:ring-0"
                                    >
                                        <option value="">Select</option>
                                        <option value="yes">Yes</option>
                                        <option value="no">No</option>
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

                            <div className="flex-1">
                                <label className="block text-[16px] font-[500] text-black mb-1">
                                    Member of any other State Welfare Board?
                                </label>
                                <div className="relative">
                                    <select
                                        className="appearance-none w-full bg-gray-100 rounded-md px-4 py-2 text-[16px] text-black/50 cursor-pointer border-0 focus:outline-none focus:ring-0"
                                    >
                                        <option value="">Select</option>
                                        <option value="yes">Yes</option>
                                        <option value="no">No</option>
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
                        </div>

                        <div className="flex gap-4">
                            <div className="flex-1">
                                <label className="block text-[16px] font-[500] text-black mb-1">
                                    Registration Date
                                </label>
                                <input
                                    type="date"
                                    className="w-full bg-gray-100 rounded-md px-4 py-2 text-[16px] text-black/50 focus:outline-none"
                                />
                            </div>
                            <div className="flex-1">
                                <label className="block text-[16px] font-[500] text-black mb-1">
                                    Time
                                </label>
                                <input
                                    type="time"
                                    className="w-full bg-gray-100 rounded-md px-4 py-2 text-[16px] text-black/50 focus:outline-none"
                                />
                            </div>
                        </div>

                        <div className="flex gap-4">
                            <div className="flex-1">
                                <label className="block text-[16px] font-[500] text-black mb-1">
                                    Do you agree with the terms?
                                </label>
                                <div className="flex gap-4">
                                    <label className="flex items-center gap-2 text-black">
                                        <input type="radio" name="agree" value="yes" />
                                        Yes
                                    </label>
                                    <label className="flex items-center gap-2 text-black">
                                        <input type="radio" name="agree" value="no" />
                                        No
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="w-[30%] bg-gray-100 p-8 flex flex-col gap-4 justify-between">
                    <div>
                        <h2 className="text-[20px] font-[600] text-[#ED7C22] mb-6">Program Details</h2>

                        <div className="mb-4">
                            <label className="block text-[16px] font-[500] text-black/50 mb-1">
                                Program Name
                            </label>
                            <div className="text-[16px] text-black font-[500]">{program.program_mnemonic}</div>
                        </div>

                        <div className="mb-4">
                            <label className="block text-[16px] font-[500] text-black/50 mb-1">
                                Program Date
                            </label>
                            <div className="text-[16px] text-black font-[500]">{program.enrolment_date}</div>
                        </div>

                        <div>
                            <label className="block text-[16px] font-[500] text-black mb-1">
                                Description
                            </label>
                            <p className="text-[16px] text-black font-[500] leading-relaxed">
                                {program.program_description}
                            </p>
                        </div>
                    </div>

                    <div className="flex gap-4 mt-4">
                        <button
                            onClick={() => router.back()}
                            className="px-6 py-2 bg-gray-200 text-gray-800 font-[500] rounded-[20px] w-full"
                        >
                            Back
                        </button>
                        <button
                            className="px-6 py-2 bg-black text-white font-[500] rounded-[20px] w-full"
                        >
                            Submit
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
