import 'server-only';
import { inflateRawSync } from 'node:zlib';
import { parse } from 'csv-parse/sync';
import { readSheet } from 'read-excel-file/node';
import { limits } from './model';

function checkWorkbook(buffer: Buffer) {
    // Check the ZIP directory before XML expansion. ZIP64 and oversized workbooks are excluded.
    const end = buffer.lastIndexOf(Buffer.from([0x50, 0x4b, 0x05, 0x06]));
    if (end < 0 || end + 22 > buffer.length) throw new Error();
    const entries = buffer.readUInt16LE(end + 10);
    let index = buffer.readUInt32LE(end + 16);
    let total = 0;
    if (entries > 128) throw new Error();
    for (let i = 0; i < entries; i++) {
        if (index + 46 > end || buffer.readUInt32LE(index) !== 0x02014b50) throw new Error();
        const compressed = buffer.readUInt32LE(index + 20);
        const size = buffer.readUInt32LE(index + 24);
        const localOffset = buffer.readUInt32LE(index + 42);
        const method = buffer.readUInt16LE(index + 10);
        const nameSize = buffer.readUInt16LE(index + 28);
        const name = buffer.toString('utf8', index + 46, index + 46 + nameSize);
        total += size;
        if (total > 16 * 1024 * 1024 || localOffset + 30 > index
            || buffer.readUInt32LE(localOffset) !== 0x04034b50 || (method !== 0 && method !== 8)) throw new Error();
        const localNameSize = buffer.readUInt16LE(localOffset + 26);
        const offset = localOffset + 30 + localNameSize + buffer.readUInt16LE(localOffset + 28);
        if (offset + compressed > index || buffer.readUInt16LE(localOffset + 8) !== method
            || buffer.toString('utf8', localOffset + 30, localOffset + 30 + localNameSize) !== name) throw new Error();
        const bytes = buffer.subarray(offset, offset + compressed);
        const data = method === 0 ? bytes : inflateRawSync(bytes, { maxOutputLength: Math.max(size, 1) });
        if (size !== data.length) throw new Error();
        if (/\.xml(?:\.rels)?$/i.test(name)) {
            const xml = data.toString('utf8');
            if (/<!DOCTYPE|<!ENTITY/i.test(xml)) throw new Error();
            if (name.startsWith('xl/worksheets/')) {
                for (const match of xml.matchAll(/<(?:\w+:)?c\b[^>]*?\br\s*=\s*["']([A-Z]+)(\d+)["']/gi)) {
                    const column = [...match[1].toUpperCase()].reduce((value, letter) => value * 26 + letter.charCodeAt(0) - 64, 0);
                    if (column > limits.columns || Number(match[2]) > limits.rows + 1) throw new Error();
                }
                for (const match of xml.matchAll(/<(?:\w+:)?row\b[^>]*?\br\s*=\s*["'](\d+)["']/gi)) {
                    if (Number(match[1]) > limits.rows + 1) throw new Error();
                }
            }
        }
        index += 46 + nameSize + buffer.readUInt16LE(index + 30) + buffer.readUInt16LE(index + 32);
    }
    if (index !== end) throw new Error();
}

export async function readImport(file: File) {
    if (/\.(pdf|png|jpe?g|webp|tiff?|heic)$/i.test(file.name)) {
        throw new Error('Use a verified CSV or XLSX. Scanned documents and images require OCR and field review first.');
    }
    if (!/\.(csv|xlsx)$/i.test(file.name) || !file.size || file.size > limits.file) {
        throw new Error('Choose a CSV or XLSX file up to 2 MB.');
    }
    const buffer = Buffer.from(await file.arrayBuffer());
    let grid: string[][];
    try {
        if (/\.xlsx$/i.test(file.name)) {
            checkWorkbook(buffer);
            const sheet = await readSheet(buffer, 1, { trim: false, parseNumber: value => value });
            grid = sheet.map(row => row.map(value => value instanceof Date ? value.toISOString().slice(0, 10) : String(value ?? '')));
        } else {
            grid = parse(new TextDecoder('utf-8', { fatal: true }).decode(buffer), {
                bom: true, skip_empty_lines: true, max_record_size: 24000, to: limits.rows + 2,
            });
        }
    } catch {
        throw new Error('The file could not be read. Check that it has a header row and consistent columns.');
    }
    const columns = grid.shift()?.map(value => value.trim()) ?? [];
    if (!columns.length || columns.length > limits.columns || columns.some(value => !value || value.length > 100) || new Set(columns).size !== columns.length) {
        throw new Error('Use up to 40 unique, non-empty column names.');
    }
    if (!grid.length || grid.length > limits.rows || grid.some(row => row.length > columns.length || row.some(value => value.length > limits.cell || value.includes('\0')))) {
        throw new Error('Use 1 to 1,000 rows and values of up to 500 characters.');
    }
    const rows = grid.map((row, i) => ({
        line: i + 2, values: columns.map((_, index) => row[index] ?? ''), excluded: false,
    })).filter(row => row.values.some(value => value.trim()));
    if (!rows.length) throw new Error('There are no populated records in the file.');
    return { columns, rows };
}
