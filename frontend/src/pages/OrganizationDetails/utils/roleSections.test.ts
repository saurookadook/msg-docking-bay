import { describe, expect, it } from 'vitest';

import { offsetParamFor, roleSectionQuery } from './roleSections';

describe('offsetParamFor', () => {
  it('names the param after the role', () => {
    expect(offsetParamFor('developer')).toBe('developer_offset');
  });
});

describe('roleSectionQuery', () => {
  const operatorQuery = roleSectionQuery({ role: 'operator' });

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
