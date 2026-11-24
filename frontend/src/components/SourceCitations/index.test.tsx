import { render, screen, within } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { mockSources, mockWikidataSource } from '@/__mocks__/catalogMocks';

import { SourceCitations } from '.';

describe('SourceCitations', () => {
  it('credits a Gundam Wiki page with its revision and licence', () => {
    render(<SourceCitations citations={[mockSources.rx782Gundam]} />);

    const sources = screen.getByRole('region', { name: 'Sources' });
    expect(within(sources).getByRole('link', { name: 'Gundam Wiki' })).toHaveAttribute(
      'href',
      'https://gundam.fandom.com/wiki/RX-78-2_Gundam',
    );
    expect(
      within(sources).getByRole('link', { name: 'revision 707889' }),
    ).toHaveAttribute(
      'href',
      'https://gundam.fandom.com/wiki/RX-78-2_Gundam?oldid=707889',
    );
    expect(within(sources).getByRole('link', { name: 'CC BY-SA 3.0' })).toHaveAttribute(
      'href',
      'https://creativecommons.org/licenses/by-sa/3.0/',
    );
  });

  it('leaves out the revision link when none was recorded', () => {
    render(<SourceCitations citations={[mockWikidataSource]} />);

    expect(screen.getByRole('link', { name: 'Wikidata' })).toBeVisible();
    expect(screen.queryByRole('link', { name: /revision/ })).not.toBeInTheDocument();
  });

  it('lists one entry per citation', () => {
    render(<SourceCitations citations={[mockSources.amuroRay, mockWikidataSource]} />);

    expect(screen.getAllByRole('listitem')).toHaveLength(2);
  });

  it('numbers each entry and gives it the id its marks link to', () => {
    render(
      <SourceCitations
        citations={[mockSources.rx782Gundam, mockWikidataSource]}
        idPrefix="dossier-source"
      />,
    );

    const entries = screen.getAllByRole('listitem');
    expect(entries.map(({ id }) => id)).toEqual([
      'dossier-source-1',
      'dossier-source-2',
    ]);
    expect(entries[1]).toHaveTextContent(/^\[2\]Wikidata/);
  });

  it('gives its entries no ids without an id prefix', () => {
    render(<SourceCitations citations={[mockSources.rx782Gundam]} />);

    expect(screen.getByRole('listitem')).not.toHaveAttribute('id');
  });

  it('renders nothing without citations', () => {
    const { container } = render(<SourceCitations citations={[]} />);

    expect(container).toBeEmptyDOMElement();
  });
});
