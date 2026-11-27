import { useId } from 'react';
import { useParams } from 'react-router';

import type { OrganizationDetailEntity } from '@/api';
import {
  CatalogDetail,
  DossierHeader,
  DossierLayout,
  DossierStrip,
  EntityLink,
  numberedCitations,
  PendingSection,
  SourceCitations,
  SpecPlate,
  VisualSlot,
  WorkAppearances,
} from '@/components';
import { NotFound } from '@/pages/NotFound';
import { fetchOrganization, useCatalogDetail, type AppState } from '@/store';
import type { AppParams } from '@/types';
import { continuityNames } from '@/utils';

import { OrgChart, RoleSuits } from './components';
import { collectCitations, SOURCE_ID_PREFIX } from './utils/citations';
import { useRoleSection } from './utils/hooks';
import { DEVELOPED, MANUFACTURED, OPERATED } from './utils/roleSections';

import './styles.css';

const selectOrganizationDetails = (appState: AppState) =>
  appState.organizations.detailsBySlug;

const PAGE_ID = 'organization-details';
const HEADING_ID = `${PAGE_ID}-title`;
const INFOBOX_HEADING_ID = `${PAGE_ID}-infobox-title`;
const FRAMING = 'Faction registry';

/** @description Registry rows the catalog does not hold yet ("DATA PENDING"). */
const PENDING_ITEMS = [
  { label: 'Type', value: null },
  { label: 'Headquarters', value: null },
  { label: 'Leaders', value: null },
  { label: 'Founded', value: null },
  { label: 'Dissolved', value: null },
];

/** @description The faction registry for a loaded organization. */
function FactionRegistry({ organization }: { organization: OrganizationDetailEntity }) {
  const weaponsHeadingID = useId();
  const manufactured = useRoleSection({
    section: MANUFACTURED,
    slug: organization.slug,
  });
  const operated = useRoleSection({ section: OPERATED, slug: organization.slug });
  const developed = useRoleSection({ section: DEVELOPED, slug: organization.slug });
  const sections = [
    { list: manufactured, section: MANUFACTURED },
    { list: operated, section: OPERATED },
    { list: developed, section: DEVELOPED },
  ];
  const { citations, cite } = numberedCitations({
    idPrefix: SOURCE_ID_PREFIX,
    sources: collectCitations({
      organization,
      sections: sections.map(({ list }) => list.items),
    }),
  });
  const { name, parent_organization } = organization;

  return (
    <DossierLayout
      header={
        <DossierHeader
          classLine={continuityNames(organization.appearances) ?? 'Faction'}
          eyebrow={FRAMING}
          headingID={HEADING_ID}
          name={name}
          nameJa={null}
        />
      }
      headingID={HEADING_ID}
      id={PAGE_ID}
      infobox={
        <aside aria-labelledby={INFOBOX_HEADING_ID}>
          <VisualSlot subject={`the ${name} insignia`} />
          <h3 className="visually-hidden" id={INFOBOX_HEADING_ID}>
            Faction data
          </h3>
          <SpecPlate
            aria-label="Registry"
            isCompact
            items={[
              {
                label: 'Parent',
                value:
                  parent_organization == null ? (
                    'None on file'
                  ) : (
                    <EntityLink kind="organization" slug={parent_organization.slug}>
                      {parent_organization.name}
                    </EntityLink>
                  ),
              },
              ...PENDING_ITEMS,
            ]}
          />
        </aside>
      }
      strip={<DossierStrip eyebrow={FRAMING} name={name} />}
    >
      <OrgChart organization={organization} />
      <WorkAppearances appearances={organization.appearances} cite={cite} />
      <section aria-labelledby={weaponsHeadingID} className="organization-weapons">
        <h3 className="stencil-label" id={weaponsHeadingID}>
          Mobile weapons
        </h3>
        {sections.map(({ list, section }) => (
          <RoleSuits cite={cite} key={section.role} list={list} section={section} />
        ))}
      </section>
      <PendingSection title="History" />
      <SourceCitations citations={citations} idPrefix={SOURCE_ID_PREFIX} />
    </DossierLayout>
  );
}

/**
 * @description An organization's faction registry, read from
 * `/organizations/:organizationSlug`. An old slug is swapped in the URL for the
 * organization's current one, keeping the search.
 */
export function OrganizationDetails() {
  const { organizationSlug = '' } = useParams<AppParams>();
  const detailState = useCatalogDetail({
    fetchDetail: fetchOrganization,
    selectDetails: selectOrganizationDetails,
    slug: organizationSlug,
  });

  return (
    <CatalogDetail
      detailState={detailState}
      id={PAGE_ID}
      kind="organization"
      loadingHeading={FRAMING}
      loadingLabel="Opening the registry"
      notFound={<NotFound />}
      slug={organizationSlug}
    >
      {(organization) => <FactionRegistry organization={organization} />}
    </CatalogDetail>
  );
}
