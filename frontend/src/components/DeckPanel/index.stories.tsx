import type { Meta, StoryObj } from '@storybook/react-vite';

import { DeckPanel } from '.';

const meta = {
  title: 'Components/DeckPanel',
  component: DeckPanel,
  args: { children: <p>MS DECK 01 · all cages standing by.</p> },
} satisfies Meta<typeof DeckPanel>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};
