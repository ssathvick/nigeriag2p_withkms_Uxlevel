export function prefixBasePath(path: string) {
    return "/portal" + path;
}

export function prefixBaseApiPath(path: string) {
    return "/api/portal" + path;
}

export function removePrefixBasePath(path: string) {
    const basePath = "/api/portal";
    return path.replace(basePath, "/");
}
