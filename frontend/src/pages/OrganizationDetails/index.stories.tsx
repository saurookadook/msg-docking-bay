import type { Meta, StoryObj } from '@storybook/react-vite';
import { Response as MirageResponse, type Server } from 'miragejs';

import { findOrganizationMock } from '@/__mocks__/organizationMocks';
import type { OrganizationResponse } from '@/api';

import { OrganizationDetails } from '.';

const meta = {
  title: 'Pages/OrganizationDetails',
  component: OrganizationDetails,
  parameters: {
    path: '/organizations/:organizationSlug',
    route: '/organizations/earth-federation',
  },
} satisfies Meta<typeof OrganizationDetails>;

export default meta;

type Story = StoryObj<typeof meta>;

/** @description The Earth Federation: one manufactured suit, two appearances. */
export const Default: Story = {};

/** @description A parent and two units, which the seed data has none of. */
export const WithOrgChart: Story = {
  parameters: {
    mirage: (server: Server) => {
      server.get('/organizations/:organization_slug', (): OrganizationResponse => ({
        data: {
          ...findOrganizationMock('earth-federation')!,
          child_organizations: [
            { name: 'Earth Federation Forces', slug: 'earth-federation-forces' },
            { name: 'Titans', slug: 'titans' },
          ],
          parent_organization: { name: 'Earth Sphere', slug: 'earth-sphere' },
        },
      }));
    },
  },
};

/** @description Zeonic: no appearances; one manufactured suit. */
export const Sparse: Story = { parameters: { route: '/organizations/zeonic' } };

/** @description An old slug: the page swaps it for the current one. */
export const OldSlug: Story = {
  parameters: { route: '/organizations/earth-federation-universal-century' },
};

export const NotFound: Story = { parameters: { route: '/organizations/titans' } };

/** @description One role section fails; the others still load. */
export const SectionFailed: Story = {
  parameters: {
    mirage: (server: Server) => {
      server.get(
        '/organizations/:organization_slug/mobile-suits',
        (_schema, request) =>
          request.queryParams['role'] === 'operator'
            ? new MirageResponse(503, {}, { detail: 'Deck offline' })
            : { data: [], meta: { limit: 50, offset: 0, total: 0 } },
      );
    },
  },
};

export const RequestFailed: Story = {
  parameters: {
    mirage: (server: Server) => {
      server.get(
        '/organizations/:organization_slug',
        () => new MirageResponse(503, {}, {}),
      );
    },
  },
};
