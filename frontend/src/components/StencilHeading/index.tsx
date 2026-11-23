import classNames from 'classnames';

import './styles.css';

export type StencilHeadingProps = React.HTMLAttributes<HTMLHeadingElement> & {
  /** @description The heading's level; pages use `2` (REACT-9). */
  level: 1 | 2 | 3;
  /** @description A small stencil line above the heading, such as `MS DECK 02`. */
  eyebrow?: string;
};

/**
 * @description A heading painted as a deck stencil. Its props go to the heading itself,
 * so `id` works with `aria-labelledby`.
 * @note The eyebrow sits outside the heading, so it is not part of the heading's name.
 */
export function StencilHeading({
  children,
  className,
  eyebrow,
  level,
  ...props
}: StencilHeadingProps) {
  const Heading = `h${level}` as const;
  const heading = (
    <Heading className={classNames('stencil-heading', className)} {...props}>
      {children}
    </Heading>
  );

  if (eyebrow == null) return heading;

  return (
    <hgroup className="stencil-heading">
      <p className="stencil-heading-eyebrow">{eyebrow}</p>
      {heading}
    </hgroup>
  );
}
