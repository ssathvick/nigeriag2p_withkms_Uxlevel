'use client';

interface Props {
    label: string;
    value: string | number;
    onChange: (value: string) => void;
    placeholder?: string;
    type?: string;
    disabled?: boolean;
}

export default function InputField({ label, value, onChange, placeholder, type = "text", disabled = false }: Props) {
    return (
        <div>
            <label
                className="block text-[16px] font-medium text-neutral-first truncate"
                title={label}
            >
                {label}
            </label>
            <input
                type={type}
                value={value}
                placeholder={placeholder}
                disabled={disabled}
                onChange={(e) => onChange(e.target.value)}
                className="mt-2 w-full border border-primary-second py-2 px-4 rounded-[10px] outline-none disabled:opacity-50 disabled:cursor-not-allowed"
            />
        </div>
    );
}
