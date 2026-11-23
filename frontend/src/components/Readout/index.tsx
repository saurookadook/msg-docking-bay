import classNames from 'classnames';

import './styles.css';

export type ReadoutProps = React.HTMLAttributes<HTMLParagraphElement> & {
  /** @description One line of terminal text. */
  children: string;
  /** @description Amber phosphor instead of green. */
  isAmber?: boolean;
  /** @description Type the line on, one character at a time, when motion is allowed. */
  isTypingOn?: boolean;
};

/** @description Inline styles plus the character count the type-on animation steps through. */
type ReadoutTextStyle = React.CSSProperties & { '--readout-chars': number };

/**
 * @description A line of deck-terminal text with scanlines.
 * @note Type-on only clips the text, so assistive technology always reads the whole
 * line, and it shows whole when motion is reduced.
 */
export function Readout({
  children,
  className,
  isAmber = false,
  isTypingOn = false,
  ...props
}: ReadoutProps) {
  const textStyle: ReadoutTextStyle = { '--readout-chars': children.length };

  return (
    <p
      className={classNames(
        'readout',
        { amber: isAmber, 'types-on': isTypingOn },
        className,
      )}
      {...props}
    >
      <span className="readout-text" style={textStyle}>
        {children}
      </span>
    </p>
  );
}
