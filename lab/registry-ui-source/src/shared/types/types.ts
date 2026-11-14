export type NestedValues<T> = T extends string
    ? T
    : T extends Record<string, unknown>
    ? NestedValues<T[keyof T]>
    : never;
