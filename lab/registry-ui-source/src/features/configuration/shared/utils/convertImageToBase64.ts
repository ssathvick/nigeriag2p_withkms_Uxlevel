export const convertImageToBase64 = (file: File | string): Promise<string> => {
    return new Promise((resolve, reject) => {
        if (typeof file === 'string') {
            resolve(file);
            return;
        }

        const reader = new FileReader();
        reader.onload = () => {
            resolve(reader.result as string);
        };
        reader.onerror = (error) => {
            reject(error);
        };
        reader.readAsDataURL(file);
    });
};
