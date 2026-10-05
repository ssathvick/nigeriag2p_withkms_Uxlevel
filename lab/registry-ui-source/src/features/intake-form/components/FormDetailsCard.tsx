
export interface FormDetailsCardProps {
    title?: string;
    description?: string;
}

export default function FormDetailsCard({
    title,
    description,
}: FormDetailsCardProps) {
    return (
        <div className="bg-secondary-second p-10 rounded-[10px] sticky top-6 w-[350px] h-[260px]">

            <h3 className="text-[20px] font-bold text-neutral-first mb-4">{title}</h3>

            <div className="text-secondary-third text-[14px] leading-[20px] flex flex-col gap-4 whitespace-pre-wrap">
                {description}
            </div>
        </div>
    );
}