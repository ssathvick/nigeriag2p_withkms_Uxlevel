export type UploadedDocument = {
    document_store_id: string;
    document_label: string;
};

// Helper function to deserialize file
export const deserializeFile = (serialized: any): File => {
    if (!serialized || !serialized.data) {
        throw new Error('Invalid serialized file');
    }

    // Convert base64 back to blob
    const byteCharacters = atob(serialized.data);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    const blob = new Blob([byteArray], { type: serialized.type });

    // Create File object from blob
    return new File([blob], serialized.name, {
        type: serialized.type,
        lastModified: serialized.lastModified,
    });
};
