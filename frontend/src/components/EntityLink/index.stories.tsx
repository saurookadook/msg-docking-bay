import type { Meta, StoryObj } from '@storybook/react-vite';

import { EntityLink } from '.';

const meta = {
  title: 'Components/EntityLink',
  component: EntityLink,
  args: { children: 'RX-78-2 Gundam', kind: 'mobileSuit', slug: 'rx-78-2-gundam' },
} satisfies Meta<typeof EntityLink>;

export default meta;

type Story = StoryObj<typeof meta>;

export const MobileSuit: Story = {};

export const Character: Story = {
  args: { children: 'Amuro Ray', kind: 'character', slug: 'amuro-ray' },
};

export const Organization: Story = {
  args: {
    children: 'Earth Federation',
    kind: 'organization',
    slug: 'earth-federation',
  },
};

export const Work: Story = {
  args: { children: 'Mobile Suit Gundam', kind: 'work', slug: 'mobile-suit-gundam' },
};

export const MechanicalDesigner: Story = {
  args: {
    children: 'Kunio Okawara',
    kind: 'mechanicalDesigner',
    slug: 'kunio-okawara',
  },
};
