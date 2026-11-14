export function getMediaUrl(imagePath: string | undefined): string {
    if (!imagePath) return "/logo.png";
    return `/portal/api/strapi/media?url=${encodeURIComponent(imagePath)}`;
}
