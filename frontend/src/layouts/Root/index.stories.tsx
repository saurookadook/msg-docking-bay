import type { Meta, StoryObj } from '@storybook/react-vite';

import { Root } from '.';

const meta = {
  title: 'Layouts/Root',
  component: Root,
  parameters: { layout: 'fullscreen' },
} satisfies Meta<typeof Root>;

export default meta;

type Story = StoryObj<typeof meta>;

/** @description The shell with an empty deck; the page goes where the outlet is. */
export const Default: Story = {};
