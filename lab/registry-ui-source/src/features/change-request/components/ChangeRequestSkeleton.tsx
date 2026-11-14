'use client';

export default function ChangeLogSkeleton() {
    return (
        <div className="rounded-[10px] bg-neutral-second px-10 py-10 pb-5 animate-pulse">
            <div
                className="grid gap-6 grid-cols-4"
            >
                <div className="space-y-3">
                    <div className="h-6 bg-secondary-third rounded w-3/4" />
                    <div className="h-4 bg-secondary-third rounded w-1/2" />
                    <div className="h-4 bg-secondary-third rounded w-1/3" />
                    <div className="h-4 bg-secondary-third rounded w-1/4" />
                </div>

                <div className="space-y-3">
                    <div className="h-6 bg-secondary-third rounded w-3/4 invisible" />
                    <div className="space-y-2 border-l-3 border-secondary-second pl-6">
                        <div className="h-4 bg-secondary-third rounded w-2/3" />
                        <div className="h-4 bg-secondary-third rounded w-1/2" />
                        <div className="h-4 bg-secondary-third rounded w-1/3" />
                    </div>
                </div>

                <div className="space-y-3">
                    <div className="flex items-center gap-1 pl-6">
                        <div className="h-6 bg-secondary-third rounded w-32" />
                        <div className="w-4 h-4 bg-secondary-third rounded" />
                    </div>
                    <div className="flex flex-col gap-2 font-semibold border-l-3 border-secondary-second pl-6">
                        <div className="h-4 bg-secondary-third rounded w-40" />
                        <div className="h-4 bg-secondary-third rounded w-36" />
                        <div className="h-4 bg-secondary-third rounded w-28" />
                    </div>
                </div>
                <div className="space-y-3">
                    <div className="h-6 bg-secondary-third rounded w-3/4 invisible" />
                    <div className="space-y-2 border-l-3 border-secondary-second pl-6">
                        <div className="h-4 bg-secondary-third rounded w-2/3" />
                        <div className="h-4 bg-secondary-third rounded w-1/2" />
                        <div className="h-4 bg-secondary-third rounded w-1/3" />
                    </div>
                </div>
            </div>

            <div className="my-4 border-t-3 border-secondary-second" />

            <div className="flex items-center justify-between">
                <div className="h-6 bg-secondary-third rounded w-24 opacity-50" />
            </div>
        </div>
    );
}
