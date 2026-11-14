'use client';

interface Props {
    label: string;
    value: string;
    onChange: (value: string) => void;
    rows?: number;
    cols?: number;
    className?: string;
    textareaClassName?: string;
    placeholder?: string;
}

export default function TextAreaField({
    label,
    value,
    onChange,
    rows = 3,
    cols,
    className = '',
    textareaClassName = '',
    placeholder
}: Props) {
    return (
        <div className={`flex flex-col ${className}`}>
            <label
                className="block text-[16px] font-medium text-neutral-first truncate"
                title={label}
            >
                {label}
            </label>
            <textarea
                value={value}
                placeholder={placeholder}
                onChange={(e) => onChange(e.target.value)}
                rows={rows}
                cols={cols}
                className={`mt-2 w-full border border-primary-second py-2 px-4 rounded-[10px] outline-none text-[16px] ${textareaClassName}`}
            />
        </div>
    );
}
