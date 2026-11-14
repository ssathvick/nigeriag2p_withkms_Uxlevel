interface TextInputProps {
    label: string;
    value: string;
    onChange: (value: string) => void;
    type?: string;
}

export function TextInput({ label, value, onChange, type = "text" }: TextInputProps) {
    return (
        <div>
            <label className="block text-[16px] text-black font-[500] mb-1">{label}</label>
            <input
                required
                type={type}
                value={value}
                onChange={(e) => onChange(e.target.value)}
                className="w-1/2 bg-gray-100 rounded-lg px-3 py-2 text-[16px] font-[500] text-black focus:outline-none"
            />
        </div>
    );
}

interface SelectInputProps {
    label: string;
    value: string;
    options: string[];
    onChange: (value: string) => void;
}

export function SelectInput({ label, value, options, onChange }: SelectInputProps) {
    return (
        <div>
            <label className="block text-[16px] text-black font-[500] mb-1">{label}</label>
            <select
                required
                value={value}
                onChange={(e) => onChange(e.target.value)}
                className="w-1/2 bg-gray-100 rounded-lg px-3 py-2 text-[16px] font-[500] text-black focus:outline-none"
            >
                <option value="">-- Select --</option>
                {options.map((opt) => (
                    <option key={opt} value={opt}>
                        {opt}
                    </option>
                ))}
            </select>
        </div>
    );
}

interface InfoProps {
    label: string;
    value?: string;
}

export function Info({ label, value }: InfoProps) {
    return (
        <div>
            <label className="block text-[16px] font-[500] text-black/50 mb-1">{label}</label>
            <div className="text-[16px] text-black font-[500]">{value || "-"}</div>
        </div>
    );
}
