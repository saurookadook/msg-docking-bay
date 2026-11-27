/**
 * @description The original blueprint silhouette of a generic mech frame, drawn on a
 * 60 × 100 grid with its feet at y = 94 and its head at y = 6.
 */
export const BLUEPRINT_PATH =
  'M24 6h12l2 8h-16zM18 16h24l4 22-6 4v14h-20v-14l-6-4zM8 18h8l-2 26h-6zM44 18h8l0 26h-6zM20 58h8l-1 36h-9zM32 58h8l1 36h-9z';

/** @description The silhouette's grid, and the rows its head and feet sit on. */
export const BLUEPRINT_GRID = { feetY: 94, headY: 6, height: 100, width: 60 } as const;
