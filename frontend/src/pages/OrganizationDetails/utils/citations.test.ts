import { describe, expect, it } from 'vitest';

import { mockSources } from '@/__mocks__/catalogMocks';
import {
  findOrganizationMobileSuitsMock,
  findOrganizationMock,
} from '@/__mocks__/organizationMocks';

import { collectCitations } from './citations';

describe('collectCitations', () => {
  it("lists the appearances, then each section's links in section order", () => {
    const citations = collectCitations({
      organization: findOrganizationMock('principality-of-zeon')!,
      sections: [
        findOrganizationMobileSuitsMock('zeonic', 'manufacturer'),
        findOrganizationMobileSuitsMock('principality-of-zeon', 'operator'),
        [],
      ],
    });

    expect(citations).toEqual([
      mockSources.principalityOfZeon,
      mockSources.principalityOfZeon,
      mockSources.ms06fZakuII,
      mockSources.ms06fZakuII,
    ]);
  });
});
