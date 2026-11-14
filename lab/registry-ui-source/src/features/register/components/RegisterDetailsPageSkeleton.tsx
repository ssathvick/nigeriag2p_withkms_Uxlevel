"use client";

interface Props {
    tabs?: any[];
}

export default function RegisterDetailsPageSkeleton({ tabs = [] }: Props) {
    return (
        <div className="animate-pulse">
            {(tabs.length === 0 && <div className="flex gap-2 px-10">
                {[1, 2, 3].map(i => (
                    <div
                        key={i}
                        className="h-11 w-32 rounded-t-[10px] bg-primary-first/50"
                    />
                ))}
            </div>)}

            <div className="grid grid-cols-12 gap-6">
                <div className="col-span-12 lg:col-span-9 space-y-6">
                    <div className="rounded-[10px] bg-neutral-second p-9.5 space-y-4 shadow-sm">
                        <div className="flex items-center gap-3">
                            <div className="h-6 w-48 rounded bg-secondary-third animate-pulse" />
                        </div>

                        <div className="space-y-2">
                            <div className="h-5 w-full rounded bg-secondary-third animate-pulse" />
                            <div className="h-5 w-5/6 rounded bg-secondary-third animate-pulse" />
                            <div className="h-5 w-4/6 rounded bg-secondary-third animate-pulse" />
                        </div>

                        <div className="grid grid-cols-2 gap-4 pt-3">
                            <div className="h-10 rounded-full bg-secondary-third animate-pulse" />
                        </div>
                    </div>

                    <div className="grid grid-cols-3 gap-6">
                        <div className="col-span-2 rounded-[10px] bg-neutral-second p-9.5 space-y-4 shadow-sm">
                            <div className="h-6 w-40 rounded bg-secondary-third animate-pulse" />
                            <div className="space-y-2">
                                <div className="h-5 w-full rounded bg-secondary-third animate-pulse" />
                                <div className="h-5 w-5/6 rounded bg-secondary-third animate-pulse" />
                                <div className="h-5 w-4/6 rounded bg-secondary-third animate-pulse" />
                            </div>
                            <div className="h-10 w-40 rounded-full bg-secondary-third animate-pulse" />
                        </div>

                        <div className="rounded-[10px] bg-neutral-second p-9.5 space-y-4 shadow-sm">
                            <div className="h-6 w-28 rounded bg-secondary-third animate-pulse" />
                            <div className="space-y-2">
                                <div className="h-5 w-full rounded bg-secondary-third animate-pulse" />
                                <div className="h-5 w-4/5 rounded bg-secondary-third animate-pulse" />
                            </div>
                            <div className="h-10 rounded-full bg-secondary-third animate-pulse" />
                        </div>
                    </div>
                </div>


                <div className="hidden lg:flex lg:col-span-3 flex-col gap-6">
                    <div className="relative rounded-[10px] bg-primary-first px-8 pt-4 pb-7 overflow-hidden animate-pulse">
                        <div className="flex items-center justify-between">
                            <div className="h-6 w-40 rounded bg-neutral-first/20" />
                            <div className="h-15 w-20 rounded-[20px] bg-neutral-first/20" />
                        </div>

                        <div className="mt-3 h-3 w-56 rounded bg-neutral-first/20" />

                        <div className="mt-25 h-10 w-32 rounded-full bg-neutral-first/20" />

                        <div className="absolute bottom-4 right-4 h-30 w-30 rounded-full bg-neutral-first/20" />
                    </div>
                    <div className="relative rounded-[10px] bg-secondary-second px-8 pt-4 pb-7 overflow-hidden animate-pulse">
                        <div className="flex items-center justify-between mb-5">
                            <div className="h-6 w-40 rounded bg-neutral-first/20" />
                            <div className="h-15 w-20 rounded-[20px] bg-neutral-first/20" />
                        </div>

                        <div className="space-y-3">
                            <div className="h-4 w-32 rounded bg-neutral-first/20" />
                            <div className="h-4 w-64 rounded bg-neutral-first/20" />
                        </div>

                        <div className="mt-4 space-y-3">
                            <div className="h-4 w-32 rounded bg-neutral-first/20" />
                            <div className="h-4 w-64 rounded bg-neutral-first/20" />
                        </div>

                        <div className="mt-6 h-10 w-32 rounded-full bg-neutral-first/20" />
                    </div>
                </div>
            </div>
        </div>
    )
}
