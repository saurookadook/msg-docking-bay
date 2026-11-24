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

/** @description A side panel's image, wider than it is tall. */
export const Landscape: Story = { args: { shape: 'landscape' } };

/** @description A small square with no caption, as in a pinned header strip. */
export const Thumbnail: Story = { args: { shape: 'thumbnail' } };
