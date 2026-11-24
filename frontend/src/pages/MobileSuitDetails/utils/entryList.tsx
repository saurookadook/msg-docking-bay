import type { Nullable } from '@/types';

/** @description One entry of an infobox plate value: a credit, a part. */
export type Entry = { content: React.ReactNode; key: string };

/** @description A plate value listing several entries, or `null` ("DATA PENDING") for none. */
export function entryList(entries: Entry[]): Nullable<React.ReactElement> {
  if (entries.length === 0) return null;
  return (
    <ul className="suit-infobox-list">
      {entries.map(({ content, key }) => (
        <li key={key}>{content}</li>
      ))}
    </ul>
  );
}
