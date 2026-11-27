import type { Meta, StoryObj } from '@storybook/react-vite';
import { Response as MirageResponse, type Server } from 'miragejs';

import { findCharacterMock } from '@/__mocks__/characterMocks';
import type { CharacterResponse } from '@/api';

import { CharacterDetails } from '.';

const meta = {
  title: 'Pages/CharacterDetails',
  component: CharacterDetails,
  parameters: { path: '/characters/:characterSlug', route: '/characters/amuro-ray' },
} satisfies Meta<typeof CharacterDetails>;

export default meta;

type Story = StoryObj<typeof meta>;

/** @description Amuro Ray: one qualified unit, two appearances. */
export const Default: Story = {};

/** @description An old slug: the page swaps it for the current one. */
export const OldSlug: Story = { parameters: { route: '/characters/amuro' } };

/** @description The Origin's Amuro: a unit with no work tag, one appearance. */
export const Sparse: Story = { parameters: { route: '/characters/amuro-ray-origin' } };

export const NotFound: Story = { parameters: { route: '/characters/char-aznable' } };

export const RequestFailed: Story = {
  parameters: {
    mirage: (server: Server) => {
      server.get('/characters/:character_slug', () => new MirageResponse(503, {}, {}));
    },
  },
};

export const Loading: Story = {
  parameters: {
    mirage: (server: Server) => {
      server.get(
        '/characters/:character_slug',
        (): CharacterResponse => ({ data: findCharacterMock('amuro-ray')! }),
        { timing: 60 * 60_000 },
      );
    },
  },
};
