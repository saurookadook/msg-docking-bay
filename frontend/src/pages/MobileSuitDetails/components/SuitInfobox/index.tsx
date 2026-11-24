import type {
  MobileSuitDetailEntity,
  MobileSuitOrganizationRole,
  MobileSuitSpecSheetEntity,
} from '@/api';
import { EntityLink, SpecPlate, VisualSlot, type SpecPlateItem } from '@/components';
import type { Nullable } from '@/types';

import type { Cite } from '../../utils/citations';
import {
  formatEpisodes,
  formatMeasurement,
  formatQuantity,
  MEASUREMENTS,
} from '../../utils/format';
import type { SpecSheetEntry } from '../../utils/specSheets';

import './styles.css';

const ROLE_LABELS: Record<MobileSuitOrganizationRole, string> = {
  manufacturer: 'Manufacturer',
  operator: 'Operator',
  developer: 'Developer',
};

const ROLES = Object.keys(ROLE_LABELS) as MobileSuitOrganizationRole[];

/** @description A plate value listing several entries, or `null` ("DATA PENDING") for none. */
function entryList(entries: { key: string; content: React.ReactNode }[]) {
  if (entries.length === 0) return null;
  return (
    <ul className="suit-infobox-list">
      {entries.map(({ content, key }) => (
        <li key={key}>{content}</li>
      ))}
    </ul>
  );
}

/** @description The work a credit is tagged with, as `(Mobile Suit Gundam)`. */
function workNote(work: Nullable<{ title: string }>) {
  return work == null ? null : (
    <span className="suit-infobox-note"> ({work.title})</span>
  );
}

/** @description The selected sheet's headline numbers and parts. */
function sheetItems(sheet: Nullable<MobileSuitSpecSheetEntity>): SpecPlateItem[] {
  const heightField =
    sheet?.overall_height_m == null && sheet?.head_height_m != null
      ? 'head_height_m'
      : 'overall_height_m';
  const isInherited = (field: MobileSuitSpecSheetEntity['inherited_fields'][number]) =>
    sheet?.inherited_fields.includes(field) ?? false;
  const partsInherited = (kind: MobileSuitSpecSheetEntity['inherited_parts'][number]) =>
    sheet?.inherited_parts.includes(kind) ?? false;
  const materials = (use: 'armor' | 'frame') =>
    entryList(
      (sheet?.materials ?? [])
        .filter(({ material_use }) => material_use === use)
        .map(({ material }) => ({ content: material.name, key: material.slug })),
    );

  return [
    {
      isInherited: isInherited(heightField),
      label: MEASUREMENTS[heightField].label,
      value: formatMeasurement({
        field: heightField,
        value: sheet?.[heightField] ?? null,
      }),
    },
    {
      isInherited: isInherited('gross_weight_kg'),
      label: MEASUREMENTS.gross_weight_kg.label,
      value: formatMeasurement({
        field: 'gross_weight_kg',
        value: sheet?.gross_weight_kg ?? null,
      }),
    },
    {
      isInherited: partsInherited('powerplants'),
      label: 'Powerplant',
      value: entryList(
        (sheet?.powerplants ?? []).map((listing) => {
          const quantity = formatQuantity(listing);
          return {
            content:
              quantity == null
                ? listing.powerplant.name
                : `${quantity} ${listing.powerplant.name}`,
            key: listing.powerplant.slug,
          };
        }),
      ),
    },
    {
      isInherited: partsInherited('materials'),
      label: 'Armor',
      value: materials('armor'),
    },
    {
      isInherited: partsInherited('materials'),
      label: 'Frame',
      value: materials('frame'),
    },
    // NOTE: a part kind is inherited whole, so a row with nothing of its own use stays pending.
  ].map((item) => ({ ...item, isInherited: item.isInherited && item.value != null }));
}

export type SuitInfoboxProps = {
  cite: Cite;
  /** @description The sheet the tabs have selected, or `null` for a suit with none. */
  selected: Nullable<SpecSheetEntry>;
  suit: MobileSuitDetailEntity;
};

/**
 * @description The dossier's side panel: the image slot, the selected spec sheet's
 * headline numbers, and who designed, built, flew and debuted the suit.
 */
export function SuitInfobox({ cite, selected, suit }: SuitInfoboxProps) {
  const sheet = selected?.sheet ?? null;
  const debuts = suit.appearances.filter(({ is_debut }) => is_debut);

  const creditItems: SpecPlateItem[] = [
    {
      label: suit.designers.length > 1 ? 'Designers' : 'Designer',
      value: entryList(
        suit.designers.map(({ mechanical_designer, source }) => ({
          content: (
            <>
              <EntityLink kind="mechanicalDesigner" slug={mechanical_designer.slug}>
                {mechanical_designer.name}
              </EntityLink>
              {cite(source)}
            </>
          ),
          key: mechanical_designer.slug,
        })),
      ),
    },
    ...ROLES.map((role) => ({
      label: ROLE_LABELS[role],
      value: entryList(
        suit.organizations
          .filter((credit) => credit.role === role)
          .map(({ organization, source, work }) => ({
            content: (
              <>
                <EntityLink kind="organization" slug={organization.slug}>
                  {organization.name}
                </EntityLink>
                {workNote(work)}
                {cite(source)}
              </>
            ),
            key: `${organization.slug}-${work?.slug ?? ''}`,
          })),
      ),
    })),
    {
      label: suit.pilots.length > 1 ? 'Pilots' : 'Pilot',
      value: entryList(
        suit.pilots.map(({ character, source, work }) => ({
          content: (
            <>
              <EntityLink kind="character" slug={character.slug}>
                {character.name}
              </EntityLink>
              {workNote(work)}
              {cite(source)}
            </>
          ),
          key: `${character.slug}-${work?.slug ?? ''}`,
        })),
      ),
    },
    {
      label: 'Debut',
      value: entryList(
        debuts.map(({ first_episode, last_episode, source, work }) => {
          const episodes = formatEpisodes({ first_episode, last_episode });
          return {
            content: (
              <>
                <EntityLink kind="work" slug={work.slug}>
                  {work.title}
                </EntityLink>
                {episodes != null && (
                  <span className="suit-infobox-note"> · {episodes}</span>
                )}
                {cite(source)}
              </>
            ),
            key: work.slug,
          };
        }),
      ),
    },
  ];

  return (
    <aside aria-labelledby="suit-infobox-title" className="suit-infobox">
      <VisualSlot subject={suit.name} />
      <h3 className="visually-hidden" id="suit-infobox-title">
        Unit data
      </h3>
      {selected != null && (
        <p className="suit-infobox-sheet stencil-label">
          {selected.label}
          {cite(selected.sheet.source)}
        </p>
      )}
      <SpecPlate aria-label="Spec summary" items={sheetItems(sheet)} />
      <SpecPlate aria-label="Credits" items={creditItems} />
    </aside>
  );
}
