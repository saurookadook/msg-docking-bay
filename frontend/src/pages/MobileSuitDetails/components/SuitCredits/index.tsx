import type {
  MobileSuitDetailEntity,
  MobileSuitOrganizationRole,
  SourceCitationEntity,
} from '@/api';
import {
  EntityLink,
  entryList,
  SpecPlate,
  type Cite,
  type SpecPlateItem,
} from '@/components';
import type { Nullable } from '@/types';
import { formatEpisodes } from '@/utils';

import './styles.css';

const ROLE_LABELS: Record<MobileSuitOrganizationRole, string> = {
  manufacturer: 'Manufacturer',
  operator: 'Operator',
  developer: 'Developer',
};

// NOTE: `Object.keys` types its result as string[]; these are ROLE_LABELS' own keys.
const ROLES = Object.keys(ROLE_LABELS) as MobileSuitOrganizationRole[];

/** @description A credit's key: the credited entity, and the work it is tagged with. */
function creditKey({ slug, work }: { slug: string; work: Nullable<{ slug: string }> }) {
  return `${slug}-${work?.slug ?? ''}`;
}

/** @description The work a credit is tagged with, as ` (Mobile Suit Gundam)`. */
function workNote(work: Nullable<{ title: string }>): Nullable<string> {
  return work == null ? null : ` (${work.title})`;
}

/** @description One credit: the credited entity's link, a muted note, and its source. */
function CreditEntry({
  children,
  cite,
  note = null,
  source,
}: {
  children: React.ReactNode;
  cite: Cite;
  note?: Nullable<string>;
  source: SourceCitationEntity;
}) {
  return (
    <>
      {children}
      {note != null && <span className="suit-credits-note">{note}</span>}
      {cite(source)}
    </>
  );
}

export type SuitCreditsProps = {
  cite: Cite;
  suit: MobileSuitDetailEntity;
};

/** @description Who designed, built and flew the suit, and where it debuted. */
export function SuitCredits({ cite, suit }: SuitCreditsProps) {
  const debuts = suit.appearances.filter(({ is_debut }) => is_debut);

  const items: SpecPlateItem[] = [
    {
      label: suit.designers.length > 1 ? 'Designers' : 'Designer',
      value: entryList(
        suit.designers.map(({ mechanical_designer, source }) => ({
          content: (
            <CreditEntry cite={cite} source={source}>
              <EntityLink kind="mechanicalDesigner" slug={mechanical_designer.slug}>
                {mechanical_designer.name}
              </EntityLink>
            </CreditEntry>
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
              <CreditEntry cite={cite} note={workNote(work)} source={source}>
                <EntityLink kind="organization" slug={organization.slug}>
                  {organization.name}
                </EntityLink>
              </CreditEntry>
            ),
            key: creditKey({ slug: organization.slug, work }),
          })),
      ),
    })),
    {
      label: suit.pilots.length > 1 ? 'Pilots' : 'Pilot',
      value: entryList(
        suit.pilots.map(({ character, source, work }) => ({
          content: (
            <CreditEntry cite={cite} note={workNote(work)} source={source}>
              <EntityLink kind="character" slug={character.slug}>
                {character.name}
              </EntityLink>
            </CreditEntry>
          ),
          key: creditKey({ slug: character.slug, work }),
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
              <CreditEntry
                cite={cite}
                note={episodes == null ? null : ` · ${episodes}`}
                source={source}
              >
                <EntityLink kind="work" slug={work.slug}>
                  {work.title}
                </EntityLink>
              </CreditEntry>
            ),
            key: work.slug,
          };
        }),
      ),
    },
  ];

  return <SpecPlate aria-label="Credits" isCompact items={items} />;
}
