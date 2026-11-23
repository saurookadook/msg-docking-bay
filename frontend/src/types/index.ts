import type { SHIFTS } from '@/constants';

export type Nullable<T> = T | null;

/** @description A deck shift, which picks the color scheme (`SHIFTS`). */
export type Shift = (typeof SHIFTS)[number];
