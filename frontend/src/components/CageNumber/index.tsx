import classNames from 'classnames';

import './styles.css';

export type CageNumberProps = React.HTMLAttributes<HTMLSpanElement> & {
  deck: number;
  cage: number;
};

const toStencilNumber = (value: number) => String(value).padStart(2, '0');

/** @description A stenciled cage plate: `MS DECK 02 · CAGE 07`. */
export function CageNumber({ cage, className, deck, ...props }: CageNumberProps) {
  return (
    <span className={classNames('cage-number', className)} {...props}>
      MS DECK {toStencilNumber(deck)} · CAGE {toStencilNumber(cage)}
    </span>
  );
}
