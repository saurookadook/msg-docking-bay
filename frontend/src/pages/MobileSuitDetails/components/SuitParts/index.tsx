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

const ARMAMENT_GROUPS: { label: string; mounts: ArmamentMount[] }[] = [
  { label: 'Fixed', mounts: ['fixed'] },
  { label: 'Handheld', mounts: ['handheld'] },
  { label: 'Optional', mounts: ['optional_fixed', 'optional_handheld'] },
];

/** @description How an optional armament is carried, shown after its name. */
const OPTIONAL_MOUNT_LABELS: Partial<Record<ArmamentMount, string>> = {
  optional_fixed: 'fixed',
  optional_handheld: 'handheld',
};

const EQUIPMENT_GROUPS: { label: string; fit: EquipmentFit }[] = [
  { label: 'Standard', fit: 'standard' },
  { label: 'Optional', fit: 'optional' },
];

/** @description A listing's note and how it is carried, as one muted line. */
function detailOf(...parts: (Nullable<string> | undefined)[]): Nullable<string> {
  const present = parts.filter((part) => part != null);
  return present.length === 0 ? null : present.join(' · ');
}

function armamentItem(listing: ArmamentListingEntity): PartItem {
  return {
    detail: detailOf(OPTIONAL_MOUNT_LABELS[listing.mount], listing.note),
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
        ARMAMENT_GROUPS.map(({ label, mounts }) => ({
          items: sheet.armaments
            .filter(({ mount }) => mounts.includes(mount))
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
                <ul aria-label={label}>
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
