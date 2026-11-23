import classNames from 'classnames';

import './styles.css';

export type DeckPanelProps = React.PropsWithChildren<
  React.HTMLAttributes<HTMLDivElement>
>;

/** @description A riveted steel panel with corner brackets, the deck's basic surface. */
export function DeckPanel({ children, className, ...props }: DeckPanelProps) {
  return (
    <div className={classNames('deck-panel', className)} {...props}>
      {children}
    </div>
  );
}
