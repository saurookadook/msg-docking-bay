import classNames from 'classnames';

import './styles.css';

export type LampStatus = 'online' | 'standby' | 'busy' | 'alert' | 'offline';

const STATUS_LABELS: Record<LampStatus, string> = {
  alert: 'Alert',
  busy: 'Working',
  offline: 'Offline',
  online: 'Online',
  standby: 'Standby',
};

export type StatusLampProps = React.HTMLAttributes<HTMLSpanElement> & {
  status: LampStatus;
};

/**
 * @description A deck status lamp with its label. The label always shows, so the status
 * never rests on color alone; `busy` spins like a warning beacon.
 * @note Defaults the label to the status's name; pass `children` to name it yourself.
 */
export function StatusLamp({ children, className, status, ...props }: StatusLampProps) {
  return (
    <span
      className={classNames('status-lamp', 'stencil-label', status, className)}
      {...props}
    >
      <span aria-hidden="true" className="status-lamp-light" />
      {children ?? STATUS_LABELS[status]}
    </span>
  );
}
