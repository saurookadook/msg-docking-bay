import type { Meta, StoryObj } from '@storybook/react-vite';

import { StatusLamp } from '.';

const meta = {
  title: 'Components/StatusLamp',
  component: StatusLamp,
  args: { status: 'online' },
} satisfies Meta<typeof StatusLamp>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Online: Story = {};

export const Standby: Story = { args: { status: 'standby' } };

/** @description Spins like a warning beacon when motion is allowed. */
export const Busy: Story = { args: { status: 'busy' } };

export const Alert: Story = { args: { status: 'alert' } };

export const Offline: Story = { args: { status: 'offline' } };

export const CustomLabel: Story = { args: { children: 'Deck systems nominal' } };
