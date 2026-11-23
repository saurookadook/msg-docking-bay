import type { Meta, StoryObj } from '@storybook/react-vite';

import { VisualSlot } from '.';

const meta = {
  title: 'Components/VisualSlot',
  component: VisualSlot,
  args: { subject: 'RX-78-2 Gundam', style: { maxInlineSize: '16rem' } },
} satisfies Meta<typeof VisualSlot>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};
