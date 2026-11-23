import classNames from 'classnames';

import './styles.css';

export type VisualSlotProps = React.HTMLAttributes<HTMLElement> & {
  /** @description What the missing image would show, such as a suit's name. */
  subject: string;
};

/**
 * @description The place an entity's image goes, holding a blueprint silhouette until
 * the images plan fills it.
 */
export function VisualSlot({ className, subject, ...props }: VisualSlotProps) {
  return (
    <figure
      aria-label={`No visual on file for ${subject}`}
      className={classNames('visual-slot', className)}
      {...props}
    >
      <svg aria-hidden="true" className="visual-slot-blueprint" viewBox="0 0 60 100">
        <path d="M24 6h12l2 8h-16zM18 16h24l4 22-6 4v14h-20v-14l-6-4zM8 18h8l-2 26h-6zM44 18h8l0 26h-6zM20 58h8l-1 36h-9zM32 58h8l1 36h-9z" />
      </svg>
      <figcaption aria-hidden="true" className="stencil-label">
        No visual on file
      </figcaption>
    </figure>
  );
}
