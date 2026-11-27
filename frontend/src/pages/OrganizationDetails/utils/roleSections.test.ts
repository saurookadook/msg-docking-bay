import { describe, expect, it } from 'vitest';

import { roleSectionQuery } from './roleSections';

describe('roleSectionQuery', () => {
  const operatorQuery = roleSectionQuery({
    offsetParam: 'operator_offset',
    role: 'operator',
  });

  it("reads the section's own offset and the page's limit, ignoring other params", () => {
    expect(
      operatorQuery(
        new URLSearchParams(
          'limit=10&offset=4&operator_offset=50&manufacturer_offset=20',
        ),
      ),
    ).toBe('limit=10&offset=50&role=operator');
  });

  it('asks for the role alone on the first page', () => {
    expect(operatorQuery(new URLSearchParams('operator_offset=%20'))).toBe(
      'role=operator',
    );
  });
});
