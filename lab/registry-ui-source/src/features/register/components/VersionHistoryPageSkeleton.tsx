'use client';

interface Props {
    tabs?: any[];
}

export default function VersionHistoryPageSkeleton({ tabs = [] }: Props) {
    return (
        <div className="animate-pulse">
            {tabs.length === 0 && (
                <div className="flex gap-2 px-10">
                    {[1, 2, 3].map(i => (
                        <div
                            key={i}
                            className="h-10 w-32 rounded-t-[10px] bg-primary-first/50"
                        />
                    ))}
                </div>
            )}

            <div className="flex gap-6">
                <div className="w-[75%] flex flex-col gap-6">
                    <div className="bg-neutral-second rounded-[10px] px-6 py-5 flex items-center gap-6">
                        <div className="flex items-center gap-3">
                            <div className="h-5 w-25 bg-secondary-third rounded" />
                            <div className="h-8.5 w-35 bg-secondary-second rounded-[10px]" />
                        </div>

                        <div className="flex items-center gap-3">
                            <div className="h-5 w-25 bg-secondary-third rounded" />
                            <div className="h-8.5 w-35 bg-secondary-second rounded-[10px]" />
                        </div>
                    </div>

                    <div className="bg-neutral-second rounded-[30px] p-9.5 space-y-5">
                        <div className="h-6 w-48 bg-secondary-third rounded" />

                        <div className="space-y-3">
                            <div className="h-5 w-full bg-secondary-second rounded" />
                            <div className="h-5 w-5/6 bg-secondary-second rounded" />
                            <div className="h-5 w-4/6 bg-secondary-second rounded" />
                        </div>

                        <div className="grid grid-cols-2 gap-4 pt-4">
                            <div className="h-10 bg-secondary-second rounded-full" />
                            <div className="h-10 bg-secondary-second rounded-full" />
                        </div>
                    </div>
                </div>

                <div className="w-[25%] space-y-4">
                    {Array.from({ length: 2 }).map((_, i) => (
                        <VerificationCardSkeleton key={i} />
                    ))}
                </div>
            </div>
        </div>
    );
}


const VerificationCardSkeleton = () => {
    return (
        <div className="bg-secondary-second/60 rounded-[10px] p-6 space-y-4 animate-pulse">
            <div className="h-4 w-24 bg-neutral-first/20 rounded" />

            <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-secondary-second rounded-full" />
                <div className="space-y-2">
                    <div className="h-5 w-40 bg-secondary-second rounded" />
                    <div className="h-3.5 w-32 bg-secondary-first rounded" />
                </div>
            </div>

            <div className="space-y-2">
                <div className="h-4 w-full bg-secondary-first rounded" />
                <div className="h-4 w-[85%] bg-secondary-first rounded" />
            </div>

            <div className="flex gap-6 pt-2">
                {[1, 2].map(i => (
                    <div key={i} className="flex items-center gap-2">
                        <div className="w-6 h-6 bg-neutral-second border rounded" />
                        <div className="h-4 w-14 bg-secondary-first rounded" />
                    </div>
                ))}
            </div>
        </div>
    );
};
