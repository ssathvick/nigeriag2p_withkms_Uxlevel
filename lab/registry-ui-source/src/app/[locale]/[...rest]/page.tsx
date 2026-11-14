import { notFound } from 'next/navigation';
// Forces a 404 for any unmatched route segment under this locale folder.
export default function CatchAllPage() {
    notFound();
}
