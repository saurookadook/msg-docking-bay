import classNames from 'classnames';

import './styles.css';

export type DossierLayoutProps = Omit<React.HTMLAttributes<HTMLElement>, 'children'> & {
  /** @description The body sections, in the main column. */
  children: React.ReactNode;
  /** @description The page's `DossierHeader`. */
  header: React.ReactNode;
  /** @description The `id` of the header's `h2`, which names the section. */
  headingID: string;
  /** @description The side panel, sticky beside the body. */
  infobox: React.ReactNode;
  /** @description The page's `DossierStrip`, pinned at phone width only. */
  strip: React.ReactNode;
};

/**
 * @description A detail page's layout: the header and body in the main column and a
 * sticky infobox beside them. At phone width it stacks strip, header, infobox, body, and
 * pins the strip instead.
 */
export function DossierLayout({
  children,
  className,
  header,
  headingID,
  infobox,
  strip,
  ...props
}: DossierLayoutProps) {
  return (
    <section
      aria-labelledby={headingID}
      className={classNames('dossier-layout', className)}
      {...props}
    >
      <div className="dossier-layout-strip">{strip}</div>
      <div className="dossier-layout-header">{header}</div>
      <div className="dossier-layout-infobox">{infobox}</div>
      <div className="dossier-layout-body">{children}</div>
    </section>
  );
}
