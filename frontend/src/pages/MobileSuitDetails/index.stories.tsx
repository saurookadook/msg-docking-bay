import type { Meta, StoryObj } from '@storybook/react-vite';
import { Response as MirageResponse, type Server } from 'miragejs';

import { mockMobileSuitDetails, mockRx782Gundam } from '@/__mocks__/mobileSuitMocks';
import type { MobileSuitResponse } from '@/api';

import { MobileSuitDetails } from '.';

const PATH = '/mobile-suits/:mobileSuitSlug';

const meta = {
  title: 'Pages/MobileSuitDetails',
  component: MobileSuitDetails,
  parameters: { path: PATH, route: `/mobile-suits/${mockRx782Gundam.slug}` },
} satisfies Meta<typeof MobileSuitDetails>;

export default meta;

type Story = StoryObj<typeof meta>;

/** @description The RX-78-2: two spec sheets, full parts, credits and lineage. */
export const Default: Story = {};

/** @description The Magnet Coating sheet, picked by `?spec=`: most values per base spec. */
export const NamedConfiguration: Story = {
  parameters: { route: `/mobile-suits/${mockRx782Gundam.slug}?spec=magnet-coating` },
};

/** @description The Zaku II: one sheet (no tabs), no powerplant on file. */
export const SingleSheet: Story = {
  parameters: { route: '/mobile-suits/ms-06f-zaku-ii' },
};

/** @description An old slug: the page swaps it for the current one. */
export const OldSlug: Story = { parameters: { route: '/mobile-suits/rx-78-2' } };

/** @description The life-size statue: few facts, no pilot. */
export const Sparse: Story = {
  parameters: { route: '/mobile-suits/rx-78f00-gundam' },
};

export const NotFound: Story = {
  parameters: { route: '/mobile-suits/turn-a-gundam' },
};

export const RequestFailed: Story = {
  parameters: {
    mirage: (server: Server) => {
      server.get(
        '/mobile-suits/:mobile_suit_slug',
        () => new MirageResponse(503, {}, {}),
      );
    },
  },
};

export const Loading: Story = {
  parameters: {
    mirage: (server: Server) => {
      server.get(
        '/mobile-suits/:mobile_suit_slug',
        (): MobileSuitResponse => ({
          data: mockMobileSuitDetails[mockRx782Gundam.slug]!,
        }),
        { timing: 60 * 60_000 },
      );
    },
  },
};
