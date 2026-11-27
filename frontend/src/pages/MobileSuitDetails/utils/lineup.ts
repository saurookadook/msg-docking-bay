import type { MobileSuitSpecSheetEntity } from '@/api';
import { BLUEPRINT_GRID } from '@/components';
import type { Nullable } from '@/types';

/** @description The human the lineup measures against, in metres. */
export const HUMAN_HEIGHT_M = 1.7;

/** @description The reference frame's height, in metres: a typical full-size suit. */
export const REFERENCE_HEIGHT_M = 18;

export type LineupHeight = {
  field: 'overall_height_m' | 'head_height_m';
  metres: number;
};

/**
 * @description The height the lineup draws: the overall height, or else the head height.
 * @returns `null` when the sheet gives neither
 */
export function lineupHeight(
  sheet: Nullable<MobileSuitSpecSheetEntity>,
): Nullable<LineupHeight> {
  if (sheet?.overall_height_m != null) {
    return { field: 'overall_height_m', metres: sheet.overall_height_m };
  }
  if (sheet?.head_height_m != null) {
    return { field: 'head_height_m', metres: sheet.head_height_m };
  }
  return null;
}

export type LineupFigure = {
  kind: 'human' | 'reference' | 'suit';
  /** @description Its height, in metres. */
  metres: number;
  width: number;
  x: number;
};

export type LineupLayout = {
  figures: LineupFigure[];
  /** @description The ground line's y; every figure stands on it. */
  groundY: number;
  /** @description The label size, in the drawing's units (metres). */
  labelSize: number;
  viewBox: string;
};

const FRAME_ASPECT =
  BLUEPRINT_GRID.width / (BLUEPRINT_GRID.feetY - BLUEPRINT_GRID.headY);

/**
 * @description Lays out a human, the 18 m reference frame and the suit side by side, in
 * metres, standing on one ground line, with room above the tallest for its label.
 */
export function lineupLayout(suitMetres: number): LineupLayout {
  const tallest = Math.max(suitMetres, REFERENCE_HEIGHT_M);
  const labelSize = tallest * 0.06;
  const gap = tallest * 0.12;
  const margin = tallest * 0.04;
  const headroom = labelSize * 2;

  const human: LineupFigure = {
    kind: 'human',
    metres: HUMAN_HEIGHT_M,
    width: HUMAN_HEIGHT_M * 0.3,
    x: margin + gap / 2,
  };
  const reference: LineupFigure = {
    kind: 'reference',
    metres: REFERENCE_HEIGHT_M,
    width: REFERENCE_HEIGHT_M * FRAME_ASPECT,
    x: human.x + human.width + gap,
  };
  const suit: LineupFigure = {
    kind: 'suit',
    metres: suitMetres,
    width: suitMetres * FRAME_ASPECT,
    x: reference.x + reference.width + gap,
  };
  const groundY = headroom + tallest;
  const width = suit.x + suit.width + margin;
  const height = groundY + labelSize * 1.5;
  const round = (value: number) => Math.round(value * 100) / 100;

  return {
    figures: [human, reference, suit],
    groundY,
    labelSize,
    viewBox: `0 0 ${round(width)} ${round(height)}`,
  };
}
