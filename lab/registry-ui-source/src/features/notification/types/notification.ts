export interface Notification {
    id: string;
    subject: string;
    body: string;
    createdAt: string;
    isRead: boolean;
    isSeen: boolean;
    isArchived: boolean;
    avatar?: string;
}
