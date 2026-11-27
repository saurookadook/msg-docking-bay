import classNames from 'classnames';
import { useId } from 'react';

import './styles.css';

export type DetailSectionProps = React.HTMLAttributes<HTMLElement> & {
  /** @description The section's `h3`, which also names the section. */
  title: string;
};

/**
 * @description One section of a detail page's body: a `section` named by its stencilled
 * `h3`, with its content stacked below.
 */
export function DetailSection({
  children,
  className,
  title,
  ...props
}: DetailSectionProps) {
  const headingID = useId();
  return (
    <section
      aria-labelledby={headingID}
      className={classNames('detail-section', className)}
      {...props}
    >
      <h3 className="stencil-label" id={headingID}>
        {title}
      </h3>
      {children}
    </section>
  );
}
