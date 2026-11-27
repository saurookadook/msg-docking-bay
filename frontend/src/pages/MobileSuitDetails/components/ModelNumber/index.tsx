import type { Nullable } from '@/types';

export type ModelNumberProps = {
  className: string;
  modelNumber: Nullable<string>;
};

/**
 * @description A suit's model number, such as `RX-78-2`, beside its name.
 * @returns nothing for a suit with no model number
 */
export function ModelNumber({ className, modelNumber }: ModelNumberProps) {
  if (modelNumber == null) return null;
  return <span className={className}>{modelNumber}</span>;
}
