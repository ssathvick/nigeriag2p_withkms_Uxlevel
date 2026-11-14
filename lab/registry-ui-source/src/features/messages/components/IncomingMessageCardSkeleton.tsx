export default function IncomingMessageCardSkeleton() {
    return (
        <div className="rounded-[10px] bg-neutral-second px-10 py-8 animate-pulse">
            <div className="grid gap-6 grid-cols-1 md:grid-cols-4 text-[16px]">
                <div className="space-y-3">
                    <div className="flex justify-between items-center">
                        <div className="h-6 w-14 bg-secondary-second rounded" />
                        <div className="h-6 w-5 bg-secondary-second rounded" />
                    </div>

                    <div className="h-5 w-48 bg-secondary-second rounded" />
                    <div className="h-5 w-44 bg-secondary-second rounded" />
                    <div className="h-5 w-56 bg-secondary-second rounded" />
                    <div className="h-5 w-64 bg-secondary-second rounded" />
                    <div className="h-5 w-52 bg-secondary-second rounded" />
                    <div className="h-5 w-64 bg-secondary-second rounded" />
                </div>

                <div className="border-l-2 border-secondary-second pl-6 space-y-3">
                    <div className="h-6 w-28 bg-secondary-second rounded" />

                    <div className="h-5 w-52 bg-secondary-second rounded" />
                    <div className="h-5 w-40 bg-secondary-second rounded" />
                    <div className="h-5 w-56 bg-secondary-second rounded" />
                    <div className="h-5 w-64 bg-secondary-second rounded" />
                </div>

                <div className="border-l-2 border-secondary-second pl-6 space-y-3">
                    <div className="flex justify-between items-center">
                        <div className="h-6 w-32 bg-secondary-second rounded" />
                        <div className="h-6 w-5 bg-secondary-second rounded" />
                    </div>

                    <div className="h-5 w-56 bg-secondary-second rounded" />
                    <div className="h-5 w-52 bg-secondary-second rounded" />
                    <div className="h-5 w-64 bg-secondary-second rounded" />
                </div>

                <div className="border-l-2 border-secondary-second pl-6 space-y-3">
                    <div className="h-6 w-24 bg-secondary-second rounded" />
                    <div className="h-5 w-48 bg-secondary-second rounded" />
                </div>
            </div>
        </div>
    );
}
