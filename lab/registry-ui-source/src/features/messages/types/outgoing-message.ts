export interface OutgoingMessage {
    outgest_id: string;
    queued_datetime: string;
    source_register: string;
    record_id: string;
    source_change_request_id: string;

    topic_resolution: string;
    topic_resolution_datetime: string;
    number_of_topics_resolved: number;
    topic_names: string[];
}
