import type { Meta, StoryObj } from '@storybook/react-vite';

import { StencilHeading } from '.';

const meta = {
  title: 'Components/StencilHeading',
  component: StencilHeading,
  args: { children: 'Cage roster', level: 2 },
} satisfies Meta<typeof StencilHeading>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const WithEyebrow: Story = { args: { eyebrow: 'MS DECK 02 · BAY A' } };

export const SubHeading: Story = { args: { children: 'Armaments', level: 3 } };
