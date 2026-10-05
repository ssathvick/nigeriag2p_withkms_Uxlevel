'use client';

import React from 'react';

export type Column<T> = {
    key: keyof T | string;
    label: string;
    render?: (item: T) => React.ReactNode;
};

interface Props<T> {
    columns: Column<T>[];
    data: T[];
    loading?: boolean;
    rowKey: (item: T) => string;
    actions?: (item: T) => React.ReactNode;
    onRowClick?: (item: T) => void;
}

export default function DataTable<T>({
    columns,
    data,
    loading,
    rowKey,
    actions,
    onRowClick
}: Props<T>) {
    const gridCols = columns.length + (actions ? 1 : 0);

    return (
        <div className="mx-7.5 bg-neutral-second rounded-[10px] p-4 overflow-hidden">
            <div
                className="grid gap-4 pb-2 px-8"
                style={{ gridTemplateColumns: `repeat(${gridCols}, minmax(0, 1fr))` }}
            >
                {columns.map((col) => (
                    <div
                        key={String(col.key)}
                        className="py-3 text-left text-base font-semibold text-primary-second"
                    >
                        {col.label}
                    </div>
                ))}

                {actions && (
                    <div className="py-3 text-left text-base font-semibold text-primary-second">
                        Actions
                    </div>
                )}
            </div>

            {loading ? (
                <div className="flex justify-center items-center py-60">
                    <img
                        src="/images/common/loading.gif"
                        className="w-12 h-12"
                        alt="Loading"
                    />
                </div>
            ) : (
                data.map((item, index) => (
                    <div
                        key={rowKey(item)}
                        onClick={() => onRowClick?.(item)}
                        className={`grid gap-4 items-center -mx-8 px-16 h-15 transition-colors ${index % 2 === 0 ? 'bg-secondary-second/25' : 'bg-neutral-second'} ${onRowClick ? 'cursor-pointer hover:bg-secondary-second/40' : ''}`}
                        style={{ gridTemplateColumns: `repeat(${gridCols}, minmax(0, 1fr))` }}
                    >
                        {columns.map((col) => {
                            const value = col.render
                                ? col.render(item)
                                : (item as any)[col.key] ?? '-';

                            return (
                                <div
                                    key={String(col.key)}
                                    className="text-[16px] font-medium truncate"
                                    title={typeof value === 'string' ? value : undefined}
                                >
                                    {value}
                                </div>
                            );
                        })}

                        {actions && (
                            <div className="flex items-center gap-6">
                                {actions(item)}
                            </div>
                        )}
                    </div>
                ))
            )}
        </div>
    );
}