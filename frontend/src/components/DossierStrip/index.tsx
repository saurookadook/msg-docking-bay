import { VisualSlot } from '@/components';
import type { Nullable } from '@/types';

import './styles.css';

export type DossierStripProps = {
  /** @description The muted line above the name: a model number, or the page's framing. */
  eyebrow: Nullable<string>;
  name: string;
};

/**
 * @description The phone-width strip pinned at the top of a detail page, keeping the
 * entity's image and name in view while the infobox scrolls away. `DossierLayout` shows
 * it at phone width only.
 * @note Hidden from assistive tech: it repeats the header.
 */
export function DossierStrip({ eyebrow, name }: DossierStripProps) {
  return (
    <div aria-hidden="true" className="dossier-strip">
      <VisualSlot className="dossier-strip-visual" shape="thumbnail" subject={name} />
      <p className="stencil-label">
        {eyebrow != null && <span className="dossier-strip-eyebrow">{eyebrow}</span>}
        {name}
      </p>
    </div>
  );
}
