import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { SpecPlate } from '.';

describe('SpecPlate', () => {
  it('pairs each label with its value', () => {
    render(<SpecPlate items={[{ label: 'Overall height', value: '18.0 m' }]} />);

    expect(screen.getByRole('term')).toHaveTextContent('Overall height');
    expect(screen.getByRole('definition')).toHaveTextContent('18.0 m');
  });

  it('marks a missing value as pending', () => {
    render(<SpecPlate items={[{ label: 'Weight', value: null }]} />);

    expect(screen.getByRole('definition')).toHaveTextContent('DATA PENDING');
  });

  it('notes a value inherited from the base spec', () => {
    render(
      <SpecPlate
        items={[{ isInherited: true, label: 'Powerplant', value: 'Minovsky' }]}
      />,
    );

    expect(screen.getByRole('definition')).toHaveTextContent('Minovskyper base spec');
  });
});
