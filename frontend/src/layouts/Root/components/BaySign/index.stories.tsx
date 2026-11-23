import type { Meta, StoryObj } from '@storybook/react-vite';

import { BaySign } from '.';

const meta = {
  title: 'Layouts/Root/BaySign',
  component: BaySign,
  args: { isCommissioned: false, kind: 'mobileSuit', label: 'Mobile Suits' },
} satisfies Meta<typeof BaySign>;

export default meta;

type Story = StoryObj<typeof meta>;

/** @description A bay whose list page doesn't exist yet. */
export const Offline: Story = {};

export const Commissioned: Story = { args: { isCommissioned: true } };

/** @description The bay the user is in: its list route is the current URL. */
export const Open: Story = {
  args: { isCommissioned: true },
  parameters: { route: '/mobile-suits' },
};
