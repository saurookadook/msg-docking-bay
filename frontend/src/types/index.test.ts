import { describe, expectTypeOf, it } from 'vitest';

import type { AppParams } from '.';

describe('AppParams', () => {
  it('names one optional slug param per entity kind', () => {
    expectTypeOf<AppParams>().toEqualTypeOf<{
      characterSlug?: string;
      mechanicalDesignerSlug?: string;
      mobileSuitSlug?: string;
      organizationSlug?: string;
      workSlug?: string;
    }>();
  });
});
