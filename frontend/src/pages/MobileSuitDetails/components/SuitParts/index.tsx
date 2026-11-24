import type {
  ArmamentListingEntity,
  ArmamentMount,
  EquipmentFit,
  MobileSuitSpecSheetEntity,
  SpecSheetPartKind,
} from '@/api';
import type { Nullable } from '@/types';

import { formatQuantity } from '../../utils/format';
import {
  MATERIAL_USE_LABELS,
  MATERIAL_USES,
  materialItems,
  powerplantItems,
  type PartItem,
} from '../../utils/sheetParts';

import './styles.css';

type PartGroup = {
  label: string;
  items: PartItem[];
};

/** @description The armament groups, in the order the panel lists them. */
const ARMAMENT_GROUPS = ['Fixed', 'Handheld', 'Optional'] as const;

/**
 * @description Each mount's group, and how an armament on it is carried when its group
 * does not already say so.
 */
const ARMAMENT_MOUNTS: Record<
  ArmamentMount,
  { carried: Nullable<string>; group: (typeof ARMAMENT_GROUPS)[number] }
> = {
  fixed: { carried: null, group: 'Fixed' },
  handheld: { carried: null, group: 'Handheld' },
  optional_fixed: { carried: 'fixed', group: 'Optional' },
  optional_handheld: { carried: 'handheld', group: 'Optional' },
};

const EQUIPMENT_GROUPS: { label: string; fit: EquipmentFit }[] = [
  { label: 'Standard', fit: 'standard' },
  { label: 'Optional', fit: 'optional' },
];

/** @description A listing's note and how it is carried, as one muted line. */
function detailOf(...parts: Nullable<string>[]): Nullable<string> {
  const present = parts.filter((part) => part != null);
  return present.length === 0 ? null : present.join(' · ');
}

function armamentItem(listing: ArmamentListingEntity): PartItem {
  return {
    detail: detailOf(ARMAMENT_MOUNTS[listing.mount].carried, listing.note),
    key: `${listing.mount}-${listing.armament.slug}`,
    name: listing.armament.name,
    quantity: formatQuantity(listing),
  };
}

/** @description The parts groups of one sheet, by kind. Empty groups are left out. */
function partKinds(sheet: MobileSuitSpecSheetEntity): {
  kind: SpecSheetPartKind;
  title: string;
  groups: PartGroup[];
}[] {
  const nonEmpty = (groups: PartGroup[]) =>
    groups.filter(({ items }) => items.length > 0);
  return [
    {
      groups: nonEmpty(
        ARMAMENT_GROUPS.map((label) => ({
          items: sheet.armaments
            .filter(({ mount }) => ARMAMENT_MOUNTS[mount].group === label)
            .map(armamentItem),
          label,
        })),
      ),
      kind: 'armaments',
      title: 'Armaments',
    },
    {
      groups: nonEmpty(
        EQUIPMENT_GROUPS.map(({ fit, label }) => ({
          items: sheet.equipment
            .filter((listing) => listing.fit === fit)
            .map(({ equipment, note }) => ({
              detail: note,
              key: equipment.slug,
              name: equipment.name,
              quantity: null,
            })),
          label,
        })),
      ),
      kind: 'equipment',
      title: 'Special equipment & features',
    },
    {
      groups: nonEmpty([
        {
          items: powerplantItems(sheet),
          label: 'Powerplant',
        },
      ]),
      kind: 'powerplants',
      title: 'Powerplant',
    },
    {
      groups: nonEmpty(
        MATERIAL_USES.map((use) => ({
          items: materialItems({ sheet, use }),
          label: MATERIAL_USE_LABELS[use],
        })),
      ),
      kind: 'materials',
      title: 'Materials',
    },
  ];
}

export type SuitPartsProps = {
  sheet: MobileSuitSpecSheetEntity;
};

/**
 * @description One spec sheet's parts: armaments by mount, equipment by fit, powerplants
 * and materials. A kind taken from the base sheet says so.
 */
export function SuitParts({ sheet }: SuitPartsProps) {
  return (
    <div className="suit-parts">
      {partKinds(sheet).map(({ groups, kind, title }) => (
        <section aria-label={title} className="suit-parts-kind" key={kind}>
          <h4 className="stencil-label">
            {title}
            {sheet.inherited_parts.includes(kind) && (
              <span className="suit-parts-inherited"> · per base spec</span>
            )}
          </h4>
          {groups.length === 0 ? (
            <p className="suit-parts-pending stencil-label">DATA PENDING</p>
          ) : (
            groups.map(({ items, label }) => (
              <div className="suit-parts-group" key={label}>
                {label !== title ? <h5 className="stencil-label">{label}</h5> : null}
                <ul aria-label={label} className="plain-list">
                  {items.map(({ detail, key, name, quantity }) => (
                    <li key={key}>
                      {quantity != null && (
                        <span className="suit-parts-quantity">{quantity}</span>
                      )}
                      <span>{name}</span>
                      {detail != null && (
                        <span className="suit-parts-detail">{detail}</span>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            ))
          )}
        </section>
      ))}
    </div>
  );
}
