import { useId } from 'react';

import type { OrganizationMobileSuitEntity } from '@/api';
import {
  mobileSuitColumns,
  RosterBody,
  rosterColumnHelper,
  type Cite,
  type RosterColumns,
} from '@/components';
import type { ListState } from '@/store';
import { citationKey } from '@/utils';

import type { RoleSection } from '../../utils/roleSections';

import './styles.css';

const helper = rosterColumnHelper<OrganizationMobileSuitEntity>();

/** @description The role section's columns, with each suit's links cited. */
function roleColumns(cite: Cite): RosterColumns<OrganizationMobileSuitEntity> {
  return [
    ...mobileSuitColumns<OrganizationMobileSuitEntity>({
      marks: ({ links }) =>
        // NOTE: one mark per distinct source, though a suit can have several links.
        [
          ...new Map(links.map(({ source }) => [citationKey(source), source])).values(),
        ].map((source) => <span key={citationKey(source)}>{cite(source)}</span>),
      suitOf: ({ mobile_suit }) => mobile_suit,
    }),
    ...helper.columns([
      helper.accessor(
        ({ links }) => {
          const titles = links.flatMap(({ work }) =>
            work == null ? [] : [work.title],
          );
          return titles.length === 0 ? 'All works' : [...new Set(titles)].join(', ');
        },
        { header: 'Works', id: 'works' },
      ),
    ]),
  ];
}

export type RoleSuitsProps = {
  cite: Cite;
  list: ListState<OrganizationMobileSuitEntity>;
  section: RoleSection;
};

/**
 * @description One role section of the organization's mobile weapons: its suits, paged
 * in the section's own URL param.
 */
export function RoleSuits({ cite, list, section }: RoleSuitsProps) {
  const headingID = useId();

  return (
    <section aria-labelledby={headingID} className="role-suits">
      <h4 className="stencil-label muted-label" id={headingID}>
        {section.title}
      </h4>
      <RosterBody
        caption={`${section.title} mobile weapons, by name`}
        columns={roleColumns(cite)}
        emptyState={<p>None on file</p>}
        getRowID={({ mobile_suit }) => mobile_suit.slug}
        list={list}
        offsetParam={section.offsetParam}
      />
    </section>
  );
}
