import classNames from 'classnames';
import { useId } from 'react';

import { SHIFTS } from '@/constants';
import { setShift, useAppStore } from '@/store';
import type { Shift } from '@/types';

import './styles.css';

const SHIFT_LABELS: Record<Shift, string> = {
  auto: 'Auto',
  day: 'Day',
  night: 'Night',
};

export type ShiftToggleProps = Omit<
  React.HTMLAttributes<HTMLFieldSetElement>,
  'onChange'
>;

/**
 * @description The deck's shift breaker: Auto follows the OS color scheme, Day forces
 * light and Night forces dark. The choice is stored for the next visit.
 */
export function ShiftToggle({ className, ...props }: ShiftToggleProps) {
  const { appState, appDispatch } = useAppStore();
  const { shift: currentShift } = appState.preferences;
  const inputIDPrefix = useId();

  function handleShiftChange(shift: Shift) {
    setShift({ dispatch: appDispatch, shift });
  }

  return (
    <fieldset className={classNames('shift-toggle', className)} {...props}>
      <legend className="stencil-label">Shift</legend>
      {SHIFTS.map((shift) => {
        const inputID = `${inputIDPrefix}-${shift}`;
        return (
          <div className="shift-toggle-option" key={shift}>
            <input
              checked={shift === currentShift}
              id={inputID}
              name={`${inputIDPrefix}-shift`}
              onChange={() => handleShiftChange(shift)}
              type="radio"
              value={shift}
            />
            <label htmlFor={inputID}>{SHIFT_LABELS[shift]}</label>
          </div>
        );
      })}
    </fieldset>
  );
}
