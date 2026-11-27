import { Navigate, useLocation } from 'react-router';

import { StatusLamp } from '@/components';
import type { DetailState } from '@/store';
import type { EntityKind } from '@/types';
import { entityPath } from '@/utils';

export type CatalogDetailProps<Detail extends { slug: string }> = {
  /** @description Renders the loaded entity's page. */
  children: (detail: Detail) => React.ReactNode;
  /** @description The slug's state, from `useCatalogDetail`. */
  detailState: DetailState<Detail> | undefined;
  /** @description The page section's `id`; its heading's is `<id>-title`. */
  id: string;
  kind: EntityKind;
  /** @description The hidden heading that names the section before the entity loads. */
  loadingHeading: string;
  /** @description What the busy lamp says while the entity loads. */
  loadingLabel: string;
  /** @description What a 404 shows: the app's `NotFound` page. */
  notFound: React.ReactNode;
  /** @description The slug in the URL, which may be an old one. */
  slug: string;
};

/**
 * @description A catalog detail page's frame: the loading lamp, the API's error, the
 * 404, and the swap of an old slug in the URL for the entity's current one (keeping the
 * search), then the loaded entity's page.
 * @note The swap does not refetch: the store keeps the detail under both slugs.
 */
export function CatalogDetail<Detail extends { slug: string }>({
  children,
  detailState,
  id,
  kind,
  loadingHeading,
  loadingLabel,
  notFound,
  slug,
}: CatalogDetailProps<Detail>) {
  const { search } = useLocation();
  const detail = detailState?.detail ?? null;
  const errorMessage = detailState?.errorMessage ?? null;
  const headingID = `${id}-title`;

  if (detailState?.isNotFound === true) return notFound;

  if (detail != null && detail.slug !== slug) {
    return (
      <Navigate
        replace
        to={{ pathname: entityPath({ kind, slug: detail.slug }), search }}
      />
    );
  }

  if (detail != null) return children(detail);

  return (
    <section aria-labelledby={headingID} id={id}>
      <h2 className="visually-hidden" id={headingID}>
        {loadingHeading}
      </h2>
      <p role="status">
        {errorMessage == null && <StatusLamp status="busy">{loadingLabel}</StatusLamp>}
      </p>
      {errorMessage != null && <p role="alert">{errorMessage}</p>}
    </section>
  );
}
