"use client";

interface FieldProps {
    label: string;
    value?: string;
    highlight?: boolean;
}

export default function AccountField({ label, value, highlight }: FieldProps) {
    return (
        <div>
            <label className="block text-[16px] font-[500] text-black/50 mb-1">{label}</label>
            <div
                className={`text-[16px] font-[500] ${highlight ? "text-[#3399FF]" : "text-black"
                    }`}
            >
                {value || "—"}
            </div>
        </div>
    );
}
