import type { Meta, StoryObj } from '@storybook/react-vite';

import { ShiftToggle } from '.';

const meta = {
  title: 'Components/ShiftToggle',
  component: ShiftToggle,
} satisfies Meta<typeof ShiftToggle>;

export default meta;

type Story = StoryObj<typeof meta>;

/** @description Pick a shift to switch the whole canvas between Day and Night. */
export const Default: Story = {};
