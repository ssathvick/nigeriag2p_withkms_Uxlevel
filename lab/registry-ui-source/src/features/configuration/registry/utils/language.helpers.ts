/**
 * Helper to read a JSON file and validate its content.
 * @param file The file to read.
 * @returns A promise that resolves to the parsed JSON object.
 */
export const readAndValidateJson = (file: File): Promise<any> => {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (event) => {
            try {
                const content = event.target?.result as string;
                const json = JSON.parse(content);

                // Basic validation: must be an object
                if (typeof json !== 'object' || json === null) {
                    reject(new Error('Invalid JSON: Must be an object'));
                    return;
                }

                resolve(json);
            } catch (error) {
                reject(new Error('Invalid JSON file'));
            }
        };
        reader.onerror = () => {
            reject(new Error('Failed to read file'));
        };
        reader.readAsText(file);
    });
};
