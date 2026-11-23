import type { Meta, StoryObj } from '@storybook/react-vite';

import { Readout } from '.';

const meta = {
  title: 'Components/Readout',
  component: Readout,
  args: { children: 'MS DECK 01 · STANDING BY' },
} satisfies Meta<typeof Readout>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Green: Story = {};

export const Amber: Story = {
  args: { children: 'CRANE 02 · IN MOTION', isAmber: true },
};

/** @description Types on when motion is allowed; reload the story to replay it. */
export const TypingOn: Story = { args: { isTypingOn: true } };
