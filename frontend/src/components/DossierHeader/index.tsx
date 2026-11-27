import { StencilHeading } from '@/components';
import type { Nullable } from '@/types';

import './styles.css';

export type DossierHeaderProps = {
  /** @description The muted line after the names, such as `Mobile Suit · Universal Century`. */
  classLine: React.ReactNode;
  /** @description The stencil above the name: a model number, or the page's framing. */
  eyebrow: string;
  /** @description The `id` of the `h2`, which names the page's section. */
  headingID: string;
  name: string;
  /** @description The Japanese name, shown with `lang="ja"` when the catalog has it. */
  nameJa: Nullable<string>;
};

/** @description A detail page's title: its stencil, name, Japanese name and class line. */
export function DossierHeader({
  classLine,
  eyebrow,
  headingID,
  name,
  nameJa,
}: DossierHeaderProps) {
  return (
    <header className="dossier-header">
      <StencilHeading eyebrow={eyebrow} id={headingID} level={2}>
        {name}
      </StencilHeading>
      {nameJa != null && (
        <p className="dossier-header-name-ja" lang="ja">
          {nameJa}
        </p>
      )}
      <p className="dossier-header-class stencil-label">{classLine}</p>
    </header>
  );
}
