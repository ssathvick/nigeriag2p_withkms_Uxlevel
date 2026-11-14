export type ComplaintStatus = "Open" | "Closed" | "In Progress";

export interface Complaint {
    id: string;
    number: string;
    status: ComplaintStatus;
    subject: string;
    description: string;
    date: string;
}
