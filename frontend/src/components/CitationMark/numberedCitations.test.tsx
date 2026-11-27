import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { mockSources } from '@/__mocks__/catalogMocks';

import { numberedCitations } from './numberedCitations';

describe('numberedCitations', () => {
  it('numbers each source once, and marks a fact with its number', () => {
    const { citations, cite } = numberedCitations({
      idPrefix: 'work-source',
      sources: [
        mockSources.rx782Gundam,
        mockSources.ms06fZakuII,
        mockSources.rx782Gundam,
      ],
    });

    expect(citations).toEqual([mockSources.rx782Gundam, mockSources.ms06fZakuII]);
    render(cite(mockSources.ms06fZakuII));
    expect(screen.getByRole('link', { name: 'Source 2' })).toHaveAttribute(
      'href',
      '#work-source-2',
    );
  });
});
