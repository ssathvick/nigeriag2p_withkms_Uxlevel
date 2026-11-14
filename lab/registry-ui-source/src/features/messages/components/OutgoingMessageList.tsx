'use client';

import OutgoingMessageCard from './OutgoingMessageCard';
import { OutgoingMessage } from '../types';

interface Props {
    messages: OutgoingMessage[];
}

export default function OutgoingMessageList({ messages }: Props) {
    return (
        <div className="space-y-4">
            {messages.map(msg => (
                <OutgoingMessageCard key={msg.outgest_id} message={msg} />
            ))}
        </div>
    );
}
