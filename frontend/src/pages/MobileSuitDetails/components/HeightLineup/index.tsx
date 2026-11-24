import { useId } from 'react';

import type { MobileSuitSpecSheetEntity } from '@/api';
import { BLUEPRINT_GRID, BLUEPRINT_PATH } from '@/components';
import type { Nullable } from '@/types';

import { formatMetres as metres, MEASUREMENTS } from '../../utils/format';
import {
  HUMAN_HEIGHT_M,
  lineupHeight,
  lineupLayout,
  REFERENCE_HEIGHT_M,
  type LineupFigure,
} from '../../utils/lineup';

import './styles.css';

const FRAME_HEIGHT = BLUEPRINT_GRID.feetY - BLUEPRINT_GRID.headY;

/** @description One figure, scaled so its feet stand on `groundY`. */
function Figure({ figure, groundY }: { figure: LineupFigure; groundY: number }) {
  const top = groundY - figure.metres;
  if (figure.kind === 'human') {
    const headRadius = figure.metres * 0.07;
    return (
      <g className="height-lineup-human">
        <circle cx={figure.x + figure.width / 2} cy={top + headRadius} r={headRadius} />
        <rect
          height={figure.metres - headRadius * 2.2}
          width={figure.width}
          x={figure.x}
          y={top + headRadius * 2.2}
        />
      </g>
    );
  }
  const scale = figure.metres / FRAME_HEIGHT;
  return (
    <path
      className={`height-lineup-${figure.kind}`}
      d={BLUEPRINT_PATH}
      transform={`translate(${figure.x} ${top - BLUEPRINT_GRID.headY * scale}) scale(${scale})`}
      vectorEffect="non-scaling-stroke"
    />
  );
}

export type HeightLineupProps = {
  name: string;
  sheet: Nullable<MobileSuitSpecSheetEntity>;
};

/**
 * @description The suit drawn to scale beside a 1.7 m human and an 18 m reference
 * frame, from the sheet's overall height, or else its head height.
 * @returns nothing when the sheet gives no height
 */
export function HeightLineup({ name, sheet }: HeightLineupProps) {
  const titleID = useId();
  const height = lineupHeight(sheet);

  if (height == null) return null;

  const { figures, groundY, labelSize, viewBox } = lineupLayout(height.metres);
  const heightLabel = MEASUREMENTS[height.field].label.toLowerCase();
  const labels = {
    human: `Human ${metres(HUMAN_HEIGHT_M)}`,
    reference: `Frame ${metres(REFERENCE_HEIGHT_M)}`,
    suit: `${name} ${metres(height.metres)}`,
  };

  return (
    <figure className="height-lineup">
      <svg aria-labelledby={titleID} role="img" viewBox={viewBox}>
        <title id={titleID}>
          {`Height lineup: ${name} at ${metres(height.metres)} (${heightLabel}), beside an ${metres(REFERENCE_HEIGHT_M)} reference frame and a ${metres(HUMAN_HEIGHT_M)} human`}
        </title>
        <line
          className="height-lineup-ground"
          vectorEffect="non-scaling-stroke"
          x1={0}
          x2="100%"
          y1={groundY}
          y2={groundY}
        />
        {figures.map((figure) => (
          <g key={figure.kind}>
            <Figure figure={figure} groundY={groundY} />
            <text
              aria-hidden="true"
              className="height-lineup-label"
              fontSize={labelSize}
              x={figure.x + figure.width / 2}
              y={groundY - figure.metres - labelSize * 0.5}
            >
              {labels[figure.kind]}
            </text>
          </g>
        ))}
      </svg>
      <figcaption className="stencil-label">Height lineup · {heightLabel}</figcaption>
    </figure>
  );
}
