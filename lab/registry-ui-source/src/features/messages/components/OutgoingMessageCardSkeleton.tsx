'use client';

export default function OutgoingMessageCardSkeleton() {
    return (
        <div className="rounded-[30px] bg-neutral-second px-10 py-8 animate-pulse">
            <div className="grid gap-6 grid-cols-1 md:grid-cols-3 text-[16px] text-neutral-first/50">
                <div className="space-y-3">
                    <div className="h-6 w-24 bg-secondary-third rounded"></div>
                    {[...Array(5)].map((_, i) => (
                        <div key={i} className="h-5 w-full max-w-45 bg-secondary-third rounded"></div>
                    ))}
                </div>

                <div className="border-l-2 border-secondary-second pl-6 space-y-3">
                    <div>
                        <div className="h-6 w-40 bg-secondary-third rounded mb-3"></div>
                        {[...Array(2)].map((_, i) => (
                            <div key={i} className="h-5 w-full max-w-35 bg-secondary-third rounded mb-2"></div>
                        ))}
                    </div>
                    <div>
                        <div className="h-6 w-24 bg-secondary-third rounded mb-3"></div>
                        <div className="h-5 w-20 bg-secondary-third rounded"></div>
                    </div>
                </div>

                <div className="border-l-2 border-secondary-second pl-6 space-y-3">
                    <div className="h-6 w-32 bg-secondary-third rounded"></div>
                    {[...Array(4)].map((_, i) => (
                        <div key={i} className="h-5 w-full max-w-40 bg-secondary-third rounded"></div>
                    ))}
                    <div className="h-5 w-20 bg-secondary-third rounded mt-2"></div>
                </div>
            </div>
        </div>
    );
}
