import { describe, expect, it } from 'vitest';

// NOTE: the raw contract is read only for its parameter bounds; types come from `@/api`.
import openapi from '@/api/generated/openapi.json';

import {
  DEFAULT_PAGE_SIZE,
  MAX_PAGE_SIZE,
  MAX_SEARCH_LENGTH,
  SEARCH_DEFAULT_LIMIT,
  SEARCH_MAX_LIMIT,
} from '.';

/** @description A `GET` route's query parameter schema, as the backend generates it. */
function parameterSchema({
  name,
  path,
}: {
  name: string;
  path: '/api/mobile-suits' | '/api/search';
}): unknown {
  const parameter = openapi.paths[path].get.parameters.find(
    (candidate) => candidate.name === name,
  );
  if (parameter === undefined) throw new Error(`${path} has no ${name} parameter`);
  return parameter.schema;
}

describe('constants mirrored from the backend', () => {
  it("match the search route's limit and q bounds", () => {
    expect(parameterSchema({ name: 'limit', path: '/api/search' })).toMatchObject({
      default: SEARCH_DEFAULT_LIMIT,
      maximum: SEARCH_MAX_LIMIT,
      minimum: 1,
    });
    expect(parameterSchema({ name: 'q', path: '/api/search' })).toMatchObject({
      anyOf: expect.arrayContaining([
        expect.objectContaining({ maxLength: MAX_SEARCH_LENGTH }),
      ]),
    });
  });

  it("match a list route's page bounds", () => {
    expect(parameterSchema({ name: 'limit', path: '/api/mobile-suits' })).toMatchObject(
      {
        default: DEFAULT_PAGE_SIZE,
        maximum: MAX_PAGE_SIZE,
        minimum: 1,
      },
    );
  });
});
