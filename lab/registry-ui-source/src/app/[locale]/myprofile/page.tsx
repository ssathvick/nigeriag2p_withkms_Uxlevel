"use client";

import LanguageSwitcher from '@/components/layout/LanguageSwitcher';
import { TopBar } from '@/components/shared';
import { useAuth } from '@/context/Authcontext';
import Image from 'next/image';
import { notFound } from 'next/navigation';


export default function MyProfile() {
    notFound()
    const { user } = useAuth()

    const profile = {
        name: user?.name,
        position: 'Registry Officer',
        phone: '+91 98765 43210',
        email: 'john.doe@registry.com',
        location: 'Bangalore, India',
        registryId: 'REG-2024-0098',
        gender: 'Male',
        dob: '12 Aug 1994',
        language: 'English',
        timezone: 'Asia/Calcutta (01/27/2026 12:59:35)',
        notifications: 'enabled',
        image: '/images/register/profile.png',
    };
    return (
        <div className="min-h-screen bg-secondary-first">
            <TopBar
                breadcrumb={[{ label: 'My Profile' }]}
                showSearch={false}
                showFilters={false}
                showPagination={false}
            />
            <div className="flex mx-7.5 bg-neutral-second rounded-[10px] min-h-150">
                <div
                    className="w-[20%] bg-primary-first bg-[url('/images/common/bg_pattern.png')] rounded-[10px] shadow-[0px_17px_21px_0px_rgba(234,187,19,0.17)] flex items-start justify-center"
                >
                    <Image
                        src={profile.image}
                        alt="Profile"
                        width={200}
                        height={200}
                        className="rounded-full object-cover mt-10"
                    />
                </div>

                <div className="w-[80%] flex-1 rounded-[30px] pt-10">
                    <div className="px-12.5 py-4">
                        <h1 className="text-[30px] font-semibold text-primary-second">{profile.name}</h1>
                        {/* <p className="text-[18px] font-semibold text-neutral-first">{profile.position}</p> */}
                    </div>

                    {/* <div className="grid grid-cols-2 gap-6 px-12.5 py-4 bg-secondary-second/25">
                        <Info label="Phone" value={profile.phone} verified />
                        <Info label="Email" value={profile.email} verified />
                    </div> */}

                    {/* <div className="grid grid-cols-2 gap-6 px-12.5 py-4">
                        <Info label="Location" value={profile.location} />
                        <Info label="Registry ID" value={profile.registryId} />
                    </div> */}

                    {/* <div className="grid grid-cols-2 gap-6 px-12.5 py-4 bg-secondary-second/25">
                        <Info label="Gender" value={profile.gender} />
                        <Info label="Date of Birth" value={profile.dob} />
                    </div> */}

                    <div className="grid grid-cols-2 gap-6 px-12.5 py-4 bg-secondary-second/25">
                        <div>
                            <p className="text-sm text-neutral-first/50 mb-1">Language</p>
                            <div className='-ml-4'>
                                <LanguageSwitcher />
                            </div>
                        </div>

                        {/* <div>
                            <p className="text-[14px] text-neutral-first/50 mb-1">Timezone</p>
                            <div className="flex items-center justify-between">
                                <p className="text-[18px] font-medium">{profile.timezone}</p>
                                <Image
                                    src="/images/common/edit.png"
                                    alt="Edit timezone"
                                    width={16}
                                    height={16}
                                    className="cursor-pointer"
                                />
                            </div>
                        </div> */}
                    </div>

                    {/* <div className="px-12.5 py-4 bg-secondary-second/25">
                        <p className="text-sm text-neutral-first/50 mb-2">Notifications</p>
                        <div className="flex gap-6">
                            <label className="flex items-center gap-2">
                                <input
                                    type="radio"
                                    name="notifications"
                                    defaultChecked={profile.notifications === 'enabled'}
                                />
                                Enabled
                            </label>

                            <label className="flex items-center gap-2">
                                <input
                                    type="radio"
                                    name="notifications"
                                    defaultChecked={profile.notifications === 'disabled'}
                                />
                                Disabled
                            </label>
                        </div>
                    </div> */}
                    {/* <div className="mt-auto pt-10 px-12.5 py-4 text-start">
                        <p className="text-[14px] text-neutral-first/50">Powered by</p>
                        <p className="text-[18px] text-neutral-first/50">OpenG2P Registry</p>
                    </div> */}
                </div>
            </div>
        </div>
    );
}

function Info({
    label,
    value,
    verified = false,
}: {
    label: string;
    value: string;
    verified?: boolean;
}) {
    return (
        <div>
            <p className="text-[14px] text-neutral-first/50 mb-1">{label}</p>
            <div className="flex items-center gap-2">
                <p className="font-medium text-[18px]">{value}</p>

                {verified && (
                    <span className="px-3 pb-0.5 pt-1.5 text-[14px] font-semibold rounded-[10px] bg-toast-success/15 text-toast-success">
                        Verified
                    </span>
                )}
            </div>
        </div>
    );
}