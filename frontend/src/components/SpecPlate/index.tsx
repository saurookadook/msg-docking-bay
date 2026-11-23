import classNames from 'classnames';

import './styles.css';

export type SpecPlateItem = {
  /** @description The row's label; labels are unique within one plate. */
  label: string;
  /** @description The value, or `null` while the catalog has none ("DATA PENDING"). */
  value: React.ReactNode;
  /** @description The value comes from the base spec sheet, not this one. */
  isInherited?: boolean;
};

export type SpecPlateProps = React.HTMLAttributes<HTMLDListElement> & {
  items: SpecPlateItem[];
};

/** @description A stamped label–value plate, such as a suit's spec sheet. */
export function SpecPlate({ className, items, ...props }: SpecPlateProps) {
  return (
    <dl className={classNames('spec-plate', className)} {...props}>
      {items.map(({ isInherited = false, label, value }) => (
        <div className="spec-plate-row" key={label}>
          <dt>{label}</dt>
          <dd className={classNames({ pending: value == null })}>
            {value ?? 'DATA PENDING'}
            {isInherited && <span className="spec-plate-inherited">per base spec</span>}
          </dd>
        </div>
      ))}
    </dl>
  );
}
