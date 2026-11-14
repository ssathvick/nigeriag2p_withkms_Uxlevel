const ApprovalListSkeleton = () => {
    return (
        <div className="rounded-[10px] space-y-4 animate-pulse">
            <div className="flex justify-between bg-primary-first/40 px-6 py-4.5 rounded-[10px] items-center">
                <div className="h-7 w-45 bg-neutral-first/30 rounded" />
            </div>

            <div className="space-y-3">
                {Array.from({ length: 2 }).map((_, i) => (
                    <ApprovalCardSkeleton key={i} />
                ))}
            </div>
        </div>
    );
};

export default ApprovalListSkeleton;

const ApprovalCardSkeleton = () => {
    return (
        <div className="bg-secondary-second/60 rounded-[10px] p-6 space-y-3 animate-pulse">
            <div className="h-3.5 w-22.5 bg-neutral-first/20 rounded-[10px]" />

            <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-secondary-second rounded-[10px]" />

                <div className="flex flex-col gap-2">
                    <div className="h-5 w-40 bg-secondary-second rounded-[10px]" />
                    <div className="h-3.5 w-35 bg-secondary-first rounded-[10px]" />
                </div>
            </div>

            <div>
                <div className="h-3.5 w-17.5 bg-secondary-second rounded-[10px] mb-2" />
                <div className="h-4 w-full bg-secondary-first rounded-[10px]" />
            </div>
        </div>
    );
};
