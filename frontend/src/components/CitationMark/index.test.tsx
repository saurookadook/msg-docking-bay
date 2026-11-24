import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { CitationMark } from '.';

describe('CitationMark', () => {
  it('links to its numbered source', () => {
    render(<CitationMark idPrefix="dossier-source" number={2} />);

    const mark = screen.getByRole('link', { name: 'Source 2' });
    expect(mark).toHaveTextContent('[2]');
    expect(mark).toHaveAttribute('href', '#dossier-source-2');
  });
});
