import classNames from 'classnames';

import { BLUEPRINT_GRID, BLUEPRINT_PATH } from './blueprint';

import './styles.css';

export type VisualSlotProps = React.HTMLAttributes<HTMLElement> & {
  /**
   * @description The slot's shape: a `portrait` card, a `landscape` panel image, or a
   * captionless square `thumbnail`.
   */
  shape?: 'landscape' | 'portrait' | 'thumbnail';
  /** @description What the missing image would show, such as a suit's name. */
  subject: string;
};

/**
 * @description The place an entity's image goes, holding a blueprint silhouette until
 * the images plan fills it.
 */
export function VisualSlot({
  className,
  shape = 'portrait',
  subject,
  ...props
}: VisualSlotProps) {
  return (
    <figure
      aria-label={`No visual on file for ${subject}`}
      className={classNames('visual-slot', `visual-slot-${shape}`, className)}
      {...props}
    >
      <svg
        aria-hidden="true"
        className="visual-slot-blueprint"
        viewBox={`0 0 ${BLUEPRINT_GRID.width} ${BLUEPRINT_GRID.height}`}
      >
        <path d={BLUEPRINT_PATH} />
      </svg>
      <figcaption aria-hidden="true" className="stencil-label">
        No visual on file
      </figcaption>
    </figure>
  );
}
