const ChangeRequestValuesTabsSkeleton = () => {
    return (
        <div className="mt-7.5">
            <div className="ml-7.5">
                <div className="px-8 py-2 text-[18px] font-medium rounded-t-[10px] bg-primary-first/50 w-50 h-11 animate-pulse" />
            </div>

            <div className="flex flex-col gap-4">
                <div className="rounded-[10px] border border-black/10 bg-neutral-second animate-pulse h-40" />
                <div className="rounded-[10px] border border-black/10 bg-neutral-second animate-pulse h-30" />
            </div>
        </div>
    );
};

export default ChangeRequestValuesTabsSkeleton;
