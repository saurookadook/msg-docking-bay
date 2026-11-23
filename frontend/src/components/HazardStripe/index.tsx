import classNames from 'classnames';

import './styles.css';

export type HazardStripeProps = React.HTMLAttributes<HTMLDivElement> & {
  /** @description Crawl continuously, as on a loading state; otherwise only on hover. */
  crawling?: boolean;
  /** @description A thick band for page edges; thin by default. */
  thick?: boolean;
};

/** @description A yellow-black hazard band. Decoration only, so it is hidden from AT. */
export function HazardStripe({
  className,
  crawling = false,
  thick = false,
  ...props
}: HazardStripeProps) {
  return (
    <div
      aria-hidden="true"
      className={classNames('hazard-stripe', { crawling, thick }, className)}
      {...props}
    />
  );
}
