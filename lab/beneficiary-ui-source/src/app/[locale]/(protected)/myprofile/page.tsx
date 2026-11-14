"use client";

import Image from "next/image";
import { useLocale } from "next-intl";
import { prefixBasePath } from "@/shared/utils/path";
import { AuthUtil } from "@/features/auth/components";
import { useAuth } from "@/context/GlobalContext";

export default function MyProfile() {
    const lang = useLocale();
    AuthUtil({ failedRedirectUrl: `/${lang}/login` });

    const { profile } = useAuth();
    const profileImage = profile?.picture || prefixBasePath("/user_image.png");

    return (
        <div className="px-[50px] py-4 min-h-screen bg-white">
            <h1 className="text-[18px] font-[600] text-gray-800 mb-4">
                My Profile
            </h1>

            <div className="relative bg-white rounded-[10px] drop-shadow-[0_4px_20px_rgba(0,0,0,0.25)] w-full overflow-hidden pb-20">
                <div className="absolute left-50 top-18">
                    <Image
                        src={profileImage}
                        alt="Profile"
                        width={144}
                        height={144}
                        className="object-cover rounded-full border-4 border-gray-200 shadow-md"
                    />
                </div>

                <div className="bg-gray-100 pl-100 pt-10 pb-10">
                    <h2 className="text-2xl font-bold text-blue-500">{profile?.name || "User"}</h2>
                    {profile?.email && (
                        <p className="text-gray-700 text-lg mt-1">{profile.email}</p>
                    )}
                </div>

                <div className="bg-white pl-100 pt-10 pb-10">
                    <section className="mb-6">
                        <h2 className="text-[20px] font-semibold text-[#ED7C22] mb-4">Personal Info</h2>
                        <div className="grid grid-cols-2 gap-x-8 gap-y-4 text-gray-800">
                            <div>
                                <p className="text-black/50 text-sm mb-1">Provider ID Type</p>
                                <p className="font-medium">{profile?.provider_unique_id_type || "-"}</p>
                            </div>
                            <div>
                                <p className="text-black/50 text-sm mb-1">Provider Unique ID</p>
                                <p className="font-medium">{profile?.provider_unique_id || "-"}</p>
                            </div>
                        </div>
                    </section>

                    <section className="mb-6">
                        <h2 className="text-[20px] font-semibold text-[#ED7C22] mb-4">Contact Info</h2>
                        <div className="grid grid-cols-2 gap-x-8 gap-y-4 text-gray-800">
                            <div>
                                <p className="text-black/50 text-sm mb-1">Phone Number</p>
                                <p className="font-medium">{profile?.phone_number || "-"}</p>
                            </div>
                            <div>
                                <p className="text-black/50 text-sm mb-1">Email ID</p>
                                <p className="font-medium">{profile?.email || "-"}</p>
                            </div>
                        </div>
                    </section>

                    <section>
                        <h2 className="text-[20px] font-semibold text-[#ED7C22] mb-4">Demographics</h2>
                        <div className="grid grid-cols-2 gap-x-8 gap-y-4 text-gray-800">
                            <div>
                                <p className="text-black/50 text-sm mb-1">Gender</p>
                                <p className="font-medium">{profile?.gender || "-"}</p>
                            </div>
                            <div>
                                <p className="text-black/50 text-sm mb-1">Date of Birth</p>
                                <p className="font-medium">{profile?.birthdate || "-"}</p>
                            </div>
                        </div>
                    </section>
                </div>
            </div>
        </div>
    );
}
