import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { mockMobileSuitDetails, mockRx782Gundam } from '@/__mocks__/mobileSuitMocks';

import { HeightLineup } from '.';

const [baseSheet] = mockMobileSuitDetails[mockRx782Gundam.slug]!.spec_sheets;

describe('HeightLineup', () => {
  it('names the three heights, saying which height of the suit it drew', () => {
    render(<HeightLineup name="Gundam" sheet={baseSheet!} />);

    expect(
      screen.getByRole('img', {
        name: 'Height lineup: Gundam at 18 m (head height), beside an 18 m reference frame and a 1.7 m human',
      }),
    ).toBeVisible();
    expect(screen.getByText('Height lineup · head height')).toBeVisible();
  });

  it('uses the overall height when the sheet has one', () => {
    render(
      <HeightLineup name="Gundam" sheet={{ ...baseSheet!, overall_height_m: 19.5 }} />,
    );

    expect(
      screen.getByRole('img', { name: /Gundam at 19\.5 m \(overall height\)/ }),
    ).toBeVisible();
  });

  it('draws nothing without a height', () => {
    const { container } = render(
      <HeightLineup name="Gundam" sheet={{ ...baseSheet!, head_height_m: null }} />,
    );

    expect(container).toBeEmptyDOMElement();
  });
});
