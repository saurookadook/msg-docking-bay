import type { Nullable } from '@/types';

/** @description One entry of a plate value: a credit, a part. */
export type PlateEntry = { content: React.ReactNode; key: string };

/** @description A plate value listing several entries, or `null` ("DATA PENDING") for none. */
export function entryList(entries: PlateEntry[]): Nullable<React.ReactElement> {
  if (entries.length === 0) return null;
  return (
    <ul className="spec-plate-list plain-list">
      {entries.map(({ content, key }) => (
        <li key={key}>{content}</li>
      ))}
    </ul>
  );
}
