import type { Meta, StoryObj } from '@storybook/react-vite';
import { Response as MirageResponse, type Server } from 'miragejs';

import { mockMobileSuits } from '@/__mocks__/mobileSuitMocks';
import type { MobileSuitsListResponse } from '@/api';

import { MobileSuitList } from '.';

const meta = {
  title: 'Pages/MobileSuitList',
  component: MobileSuitList,
  parameters: { route: '/mobile-suits' },
} satisfies Meta<typeof MobileSuitList>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};

/** @description Two to a page, filtered to one continuity, to show the page links. */
export const Paged: Story = {
  parameters: { route: '/mobile-suits?continuity=universal-century&limit=2' },
};

/** @description An old work slug: the chip shows the work's title. */
export const FilteredByWork: Story = {
  parameters: { route: '/mobile-suits?work=msg' },
};

export const Empty: Story = { parameters: { route: '/mobile-suits?q=turn-a' } };

export const Loading: Story = {
  parameters: {
    mirage: (server: Server) => {
      server.get(
        '/mobile-suits',
        (): MobileSuitsListResponse => ({
          data: [...mockMobileSuits],
          meta: { limit: 50, offset: 0, total: 4 },
        }),
        { timing: 60 * 60_000 },
      );
    },
  },
};

export const Failed: Story = {
  parameters: {
    mirage: (server: Server) => {
      server.get(
        '/mobile-suits',
        () => new MirageResponse(503, {}, { detail: 'Deck offline' }),
      );
    },
  },
};
