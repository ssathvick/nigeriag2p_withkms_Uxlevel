'use client';

import { useRouter } from 'next/navigation';
import { IncomingMessageCard } from '@/features/messages/components';
import { IncomingMessage } from '@/features/messages/types';


interface Props {
    messages: IncomingMessage[];
}

export default function IncomingMessageList({ messages }: Props) {
    const router = useRouter();

    return (
        <div className="space-y-4">
            {messages.map(msg => (
                <IncomingMessageCard
                    key={msg.ingest_id}
                    message={msg}
                />
            ))}
        </div>
    );
}
