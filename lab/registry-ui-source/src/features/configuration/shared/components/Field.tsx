'use client';

interface FieldProps {
    label: string;
    value?: any;
    className?: string;
    layout?: 'row' | 'column';
}

export default function Field({
    label,
    value,
    className = '',
    layout = 'row',
}: FieldProps) {
    if (layout === 'column') {
        return (
            <div className={`py-2 ${className}`}>
                <span className="text-neutral-first/50 text-[16px] font-medium block mb-2">
                    {label}
                </span>
                <div className="text-neutral-first text-[16px] font-normal bg-neutral-second px-4 py-2 rounded-[10px] border border-secondary-first break-all">
                    {value ?? '-'}
                </div>
            </div>
        );
    }

    return (
        <div className={`grid grid-cols-[1.2fr_2fr] gap-4 py-2 ${className}`}>
            <span className="text-neutral-first/50 text-[16px] font-medium truncate" title={label}>
                {label}
            </span>
            <div className="text-neutral-first text-[16px] font-normal break-all">
                {value ?? '-'}
            </div>
        </div>
    );
}
