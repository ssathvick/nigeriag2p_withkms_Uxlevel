'use client';

interface PayloadViewProps {
    data: any;
}

export default function PayloadView({ data }: PayloadViewProps) {
    return (
        <div className="flex-1 bg-secondary-second/50 px-6 py-3 overflow-y-auto overflow-x-auto message-json-scroll">
            <pre className="text-[14px] text-neutral-first whitespace-pre">
                {JSON.stringify(data, null, 2)}
            </pre>
        </div>
    );
}
